#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Export management module for AccessChk GUI.

This module provides the ExportManager class for exporting scan results
to multiple formats (CSV, JSON, XML).

Classes:
    ExportManager: Static methods for exporting logs to various formats
"""

import csv
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict
from pathlib import Path
import logging

from src.utils import extract_first_path

__all__ = ['ExportManager']

logger = logging.getLogger(__name__)


class ExportManager:
    """Manager for multi-format exports of scan results.
    
    Provides static methods to export scan logs to CSV, JSON, and XML
    formats with proper encoding and structure.
    
    Supported formats:
        - CSV: Comma-separated values with headers
        - JSON: Structured JSON with metadata
        - XML: XML tree with proper attributes
        
    Example:
        >>> logs = [
        ...     {"line": "RW C:\\Windows", "write": True, "err": False},
        ...     {"line": "R  C:\\Program Files", "write": False, "err": False}
        ... ]
        >>> ExportManager.export_to_json(logs, "scan_results.json")
        >>> ExportManager.export_to_csv(logs, "scan_results.csv")
        >>> ExportManager.export_to_xml(logs, "scan_results.xml")
    """
    
    @staticmethod
    def export_to_csv(logs: List[Dict], filepath: str) -> None:
        """Export logs to CSV format.
        
        Creates a CSV file with columns: timestamp, type, permissions, path, user.
        Each log entry is converted to a row with extracted information.
        
        Args:
            logs: List of log dictionaries with 'line', 'write', 'err' keys
            filepath: Destination CSV file path
            
        Raises:
            IOError: If file cannot be written
            PermissionError: If no write access to destination
            
        Example:
            >>> logs = [{"line": "RW C:\\\\Windows", "write": True, "err": False}]
            >>> ExportManager.export_to_csv(logs, "results.csv")
            # Creates: timestamp,type,permissions,path,user
            #          2024-01-15T10:30:00,write,RW C:\\Windows,C:\\Windows,current_user
        """
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['timestamp', 'type', 'permissions', 'path', 'user']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for log in logs:
                    line = log['line']
                    writer.writerow({
                        'timestamp': datetime.now().isoformat(),
                        'type': 'error' if log['err'] else ('write' if log['write'] else 'read'),
                        'permissions': line,
                        'path': extract_first_path(line) or '',
                        'user': 'current_user'
                    })
            
            logger.info(f"Exported {len(logs)} entries to CSV: {filepath}")
            
        except (IOError, OSError, csv.Error) as e:
            logger.error(f"Failed to export CSV to {filepath}: {e}")
            raise
    
    @staticmethod
    def export_to_json(logs: List[Dict], filepath: str) -> None:
        """Export logs to JSON format.
        
        Creates a structured JSON file with metadata and entries array.
        Includes export timestamp, total count, and detailed entries.
        
        Args:
            logs: List of log dictionaries with 'line', 'write', 'err' keys
            filepath: Destination JSON file path
            
        Raises:
            IOError: If file cannot be written
            JSONEncodeError: If data cannot be serialized
            
        Example:
            >>> logs = [{"line": "RW C:\\Windows", "write": True, "err": False}]
            >>> ExportManager.export_to_json(logs, "results.json")
            # Creates: {
            #   "export_timestamp": "2024-01-15T10:30:00",
            #   "total_entries": 1,
            #   "entries": [
            #     {
            #       "line": "RW C:\\Windows",
            #       "has_write": true,
            #       "is_error": false,
            #       "path": "C:\\Windows",
            #       "timestamp": "2024-01-15T10:30:00"
            #     }
            #   ]
            # }
        """
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'total_entries': len(logs),
                'entries': []
            }
            
            for log in logs:
                entry = {
                    'line': log['line'],
                    'has_write': log['write'],
                    'is_error': log['err'],
                    'path': extract_first_path(log['line']),
                    'timestamp': datetime.now().isoformat()
                }
                export_data['entries'].append(entry)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(logs)} entries to JSON: {filepath}")
            
        except (IOError, OSError, json.JSONEncodeError) as e:
            logger.error(f"Failed to export JSON to {filepath}: {e}")
            raise
    
    @staticmethod
    def export_to_xml(logs: List[Dict], filepath: str) -> None:
        """Export logs to XML format.
        
        Creates an XML document with root element 'accesschk_scan' and
        child 'entry' elements for each log line. Includes metadata
        attributes and path extraction.
        
        Args:
            logs: List of log dictionaries with 'line', 'write', 'err' keys
            filepath: Destination XML file path
            
        Raises:
            IOError: If file cannot be written
            ET.ParseError: If XML generation fails
            
        Example:
            >>> logs = [{"line": "RW C:\\\\Windows", "write": True, "err": False}]
            >>> ExportManager.export_to_xml(logs, "results.xml")
            # Creates: <?xml version='1.0' encoding='utf-8'?>
            # <accesschk_scan timestamp="2024-01-15T10:30:00" total_entries="1">
            #   <entry has_write="True" is_error="False">
            #     <line>RW C:\\Windows</line>
            #     <path>C:\\Windows</path>
            #   </entry>
            # </accesschk_scan>
        """
        try:
            root = ET.Element('accesschk_scan')
            root.set('timestamp', datetime.now().isoformat())
            root.set('total_entries', str(len(logs)))
            
            for log in logs:
                entry = ET.SubElement(root, 'entry')
                entry.set('has_write', str(log['write']))
                entry.set('is_error', str(log['err']))
                
                line_elem = ET.SubElement(entry, 'line')
                line_elem.text = log['line']
                
                path = extract_first_path(log['line'])
                if path:
                    path_elem = ET.SubElement(entry, 'path')
                    path_elem.text = path
            
            tree = ET.ElementTree(root)
            tree.write(filepath, encoding='utf-8', xml_declaration=True)
            
            logger.info(f"Exported {len(logs)} entries to XML: {filepath}")
            
        except (IOError, OSError, ET.ParseError) as e:
            logger.error(f"Failed to export XML to {filepath}: {e}")
            raise

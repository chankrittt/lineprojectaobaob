"""
LINE Flex Message Templates

Provides pre-built Flex Message structures for:
- File upload confirmation
- Processing results
- Search results
- File details
- Statistics
"""

from typing import Dict, List, Optional, Any
from datetime import datetime


class FlexMessageTemplates:
    """Factory for creating Flex Messages"""

    @staticmethod
    def file_upload_confirmation(
        filename: str,
        file_size: int,
        file_type: str,
        file_id: str
    ) -> Dict:
        """
        Create Flex Message for file upload confirmation

        Args:
            filename: Original filename
            file_size: File size in bytes
            file_type: MIME type
            file_id: File UUID

        Returns:
            Flex Message JSON structure
        """
        # Format file size
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"

        return {
            "type": "bubble",
            "hero": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "📤 อัปโหลดสำเร็จ",
                        "size": "xl",
                        "weight": "bold",
                        "color": "#27AE60"
                    }
                ],
                "backgroundColor": "#E8F8F5",
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": filename,
                        "size": "md",
                        "weight": "bold",
                        "wrap": True,
                        "color": "#2C3E50"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "ขนาด",
                                        "color": "#7F8C8D",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": size_str,
                                        "wrap": True,
                                        "color": "#2C3E50",
                                        "size": "sm",
                                        "flex": 2
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "ประเภท",
                                        "color": "#7F8C8D",
                                        "size": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "text",
                                        "text": file_type.split('/')[-1].upper(),
                                        "wrap": True,
                                        "color": "#2C3E50",
                                        "size": "sm",
                                        "flex": 2
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "separator",
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "md",
                        "contents": [
                            {
                                "type": "text",
                                "text": "⏳ กำลังประมวลผลด้วย AI...",
                                "size": "sm",
                                "color": "#95A5A6",
                                "align": "center"
                            }
                        ]
                    }
                ]
            }
        }

    @staticmethod
    def processing_complete(
        filename: str,
        ai_filename: str,
        summary: str,
        tags: List[str],
        file_id: str,
        thumbnail_url: Optional[str] = None
    ) -> Dict:
        """
        Create Flex Message for completed processing

        Args:
            filename: Original filename
            ai_filename: AI-generated filename
            summary: File summary
            tags: List of tags
            file_id: File UUID
            thumbnail_url: Optional thumbnail URL

        Returns:
            Flex Message JSON structure
        """
        # Build tag boxes
        tag_contents = []
        for tag in tags[:5]:  # Limit to 5 tags
            tag_contents.append({
                "type": "text",
                "text": f"#{tag}",
                "size": "xs",
                "color": "#3498DB",
                "flex": 0
            })
            tag_contents.append({
                "type": "separator",
                "margin": "xs"
            })

        # Remove last separator
        if tag_contents:
            tag_contents.pop()

        hero_content = {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "✅ ประมวลผลเสร็จแล้ว",
                    "size": "xl",
                    "weight": "bold",
                    "color": "#FFFFFF"
                }
            ],
            "backgroundColor": "#27AE60",
            "paddingAll": "20px"
        }

        # Add thumbnail if available
        if thumbnail_url:
            hero_content = {
                "type": "image",
                "url": thumbnail_url,
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover"
            }

        return {
            "type": "bubble",
            "hero": hero_content,
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "AI แนะนำชื่อไฟล์",
                        "size": "xs",
                        "color": "#7F8C8D",
                        "margin": "none"
                    },
                    {
                        "type": "text",
                        "text": ai_filename,
                        "size": "md",
                        "weight": "bold",
                        "wrap": True,
                        "color": "#2C3E50",
                        "margin": "xs"
                    },
                    {
                        "type": "separator",
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": "สรุปเนื้อหา",
                        "size": "xs",
                        "color": "#7F8C8D",
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": summary[:150] + ("..." if len(summary) > 150 else ""),
                        "size": "sm",
                        "wrap": True,
                        "color": "#34495E",
                        "margin": "xs"
                    },
                    {
                        "type": "separator",
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": "แท็ก",
                        "size": "xs",
                        "color": "#7F8C8D",
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "xs",
                        "spacing": "xs",
                        "contents": tag_contents if tag_contents else [
                            {
                                "type": "text",
                                "text": "ไม่มีแท็ก",
                                "size": "xs",
                                "color": "#95A5A6"
                            }
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": "ดูรายละเอียด",
                            "uri": f"https://example.com/files/{file_id}"
                        },
                        "color": "#3498DB"
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "height": "sm",
                        "action": {
                            "type": "postback",
                            "label": "แชร์ไฟล์",
                            "data": f"action=share&file_id={file_id}"
                        }
                    }
                ]
            }
        }

    @staticmethod
    def search_results(
        query: str,
        files: List[Dict[str, Any]],
        total_count: int
    ) -> Dict:
        """
        Create Flex Message for search results

        Args:
            query: Search query
            files: List of file dictionaries
            total_count: Total number of results

        Returns:
            Flex Message JSON structure
        """
        # Build file list
        file_contents = []
        for file in files[:5]:  # Show max 5 results
            file_contents.append({
                "type": "box",
                "layout": "horizontal",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "flex": 1,
                        "contents": [
                            {
                                "type": "text",
                                "text": file.get('final_filename', 'Unknown'),
                                "size": "sm",
                                "weight": "bold",
                                "wrap": True,
                                "color": "#2C3E50"
                            },
                            {
                                "type": "text",
                                "text": file.get('summary', '')[:80] + "..." if len(file.get('summary', '')) > 80 else file.get('summary', ''),
                                "size": "xs",
                                "color": "#7F8C8D",
                                "wrap": True,
                                "margin": "xs"
                            }
                        ]
                    },
                    {
                        "type": "button",
                        "flex": 0,
                        "height": "sm",
                        "style": "link",
                        "action": {
                            "type": "uri",
                            "label": "เปิด",
                            "uri": f"https://example.com/files/{file.get('id')}"
                        }
                    }
                ]
            })

            file_contents.append({
                "type": "separator",
                "margin": "md"
            })

        # Remove last separator
        if file_contents:
            file_contents.pop()

        return {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "🔍 ผลการค้นหา",
                        "size": "xl",
                        "weight": "bold",
                        "color": "#FFFFFF"
                    },
                    {
                        "type": "text",
                        "text": f'"{query}"',
                        "size": "sm",
                        "color": "#ECF0F1",
                        "margin": "xs"
                    }
                ],
                "backgroundColor": "#3498DB",
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"พบ {total_count} ไฟล์",
                        "size": "xs",
                        "color": "#7F8C8D",
                        "margin": "none"
                    },
                    {
                        "type": "separator",
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "md",
                        "spacing": "md",
                        "contents": file_contents if file_contents else [
                            {
                                "type": "text",
                                "text": "ไม่พบผลลัพธ์",
                                "size": "sm",
                                "color": "#95A5A6",
                                "align": "center"
                            }
                        ]
                    }
                ]
            }
        }

    @staticmethod
    def statistics(
        total_files: int,
        total_size: int,
        by_type: Dict[str, int],
        recent_uploads: int
    ) -> Dict:
        """
        Create Flex Message for user statistics

        Args:
            total_files: Total number of files
            total_size: Total storage used in bytes
            by_type: File count by type
            recent_uploads: Files uploaded in last 7 days

        Returns:
            Flex Message JSON structure
        """
        # Format storage size
        if total_size < 1024 * 1024:
            size_str = f"{total_size / 1024:.1f} KB"
        elif total_size < 1024 * 1024 * 1024:
            size_str = f"{total_size / (1024 * 1024):.1f} MB"
        else:
            size_str = f"{total_size / (1024 * 1024 * 1024):.2f} GB"

        # Build type breakdown
        type_contents = []
        for file_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True)[:5]:
            type_contents.append({
                "type": "box",
                "layout": "baseline",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "text",
                        "text": file_type.upper(),
                        "color": "#7F8C8D",
                        "size": "sm",
                        "flex": 1
                    },
                    {
                        "type": "text",
                        "text": f"{count} ไฟล์",
                        "wrap": True,
                        "color": "#2C3E50",
                        "size": "sm",
                        "flex": 1,
                        "align": "end"
                    }
                ]
            })

        return {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "📊 สถิติการใช้งาน",
                        "size": "xl",
                        "weight": "bold",
                        "color": "#FFFFFF"
                    }
                ],
                "backgroundColor": "#9B59B6",
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 1,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": str(total_files),
                                        "size": "xxl",
                                        "weight": "bold",
                                        "color": "#3498DB",
                                        "align": "center"
                                    },
                                    {
                                        "type": "text",
                                        "text": "ไฟล์ทั้งหมด",
                                        "size": "xs",
                                        "color": "#7F8C8D",
                                        "align": "center",
                                        "margin": "xs"
                                    }
                                ]
                            },
                            {
                                "type": "separator"
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 1,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": size_str,
                                        "size": "lg",
                                        "weight": "bold",
                                        "color": "#E74C3C",
                                        "align": "center"
                                    },
                                    {
                                        "type": "text",
                                        "text": "พื้นที่ใช้",
                                        "size": "xs",
                                        "color": "#7F8C8D",
                                        "align": "center",
                                        "margin": "xs"
                                    }
                                ]
                            }
                        ],
                        "margin": "none"
                    },
                    {
                        "type": "separator",
                        "margin": "lg"
                    },
                    {
                        "type": "text",
                        "text": "ประเภทไฟล์",
                        "size": "sm",
                        "weight": "bold",
                        "color": "#2C3E50",
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "sm",
                        "spacing": "sm",
                        "contents": type_contents if type_contents else [
                            {
                                "type": "text",
                                "text": "ยังไม่มีไฟล์",
                                "size": "xs",
                                "color": "#95A5A6",
                                "align": "center"
                            }
                        ]
                    },
                    {
                        "type": "separator",
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "baseline",
                        "spacing": "sm",
                        "margin": "md",
                        "contents": [
                            {
                                "type": "text",
                                "text": "อัปโหลด 7 วันที่แล้ว",
                                "color": "#7F8C8D",
                                "size": "sm",
                                "flex": 2
                            },
                            {
                                "type": "text",
                                "text": f"{recent_uploads} ไฟล์",
                                "wrap": True,
                                "color": "#27AE60",
                                "size": "sm",
                                "flex": 1,
                                "align": "end",
                                "weight": "bold"
                            }
                        ]
                    }
                ]
            }
        }

    @staticmethod
    def help_menu() -> Dict:
        """
        Create Flex Message for help/commands menu

        Returns:
            Flex Message JSON structure
        """
        return {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "ℹ️ คำสั่งที่ใช้ได้",
                        "size": "xl",
                        "weight": "bold",
                        "color": "#FFFFFF"
                    }
                ],
                "backgroundColor": "#16A085",
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "text",
                                "text": "/search <คำค้นหา>",
                                "size": "sm",
                                "weight": "bold",
                                "color": "#2C3E50"
                            },
                            {
                                "type": "text",
                                "text": "ค้นหาไฟล์จากชื่อ เนื้อหา หรือแท็ก",
                                "size": "xs",
                                "color": "#7F8C8D",
                                "wrap": True
                            }
                        ]
                    },
                    {
                        "type": "separator"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "text",
                                "text": "/list",
                                "size": "sm",
                                "weight": "bold",
                                "color": "#2C3E50"
                            },
                            {
                                "type": "text",
                                "text": "แสดงไฟล์ล่าสุด 10 ไฟล์",
                                "size": "xs",
                                "color": "#7F8C8D",
                                "wrap": True
                            }
                        ]
                    },
                    {
                        "type": "separator"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "text",
                                "text": "/stats",
                                "size": "sm",
                                "weight": "bold",
                                "color": "#2C3E50"
                            },
                            {
                                "type": "text",
                                "text": "แสดงสถิติการใช้งานและพื้นที่เก็บข้อมูล",
                                "size": "xs",
                                "color": "#7F8C8D",
                                "wrap": True
                            }
                        ]
                    },
                    {
                        "type": "separator"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "text",
                                "text": "ส่งไฟล์/รูปภาพ/วิดีโอ",
                                "size": "sm",
                                "weight": "bold",
                                "color": "#2C3E50"
                            },
                            {
                                "type": "text",
                                "text": "ส่งไฟล์มาเพื่ออัปโหลดและประมวลผลด้วย AI",
                                "size": "xs",
                                "color": "#7F8C8D",
                                "wrap": True
                            }
                        ]
                    }
                ]
            }
        }


# Convenience instance
flex_templates = FlexMessageTemplates()

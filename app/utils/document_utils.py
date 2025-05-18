import tempfile
import os
from docx import Document
from fpdf import FPDF
from aiogram.types import FSInputFile
from aiogram import Bot
import textwrap

import logging
import time

logging.getLogger('fontTools.subset').disabled = True

async def convert_and_send_text(bot: Bot, user_id: int, text: str, format_type: str) -> bool:
    """Конвертирует текст в указанный формат и отправляет пользователю"""
    
    temp_path = None
    try:
        if not text or not text.strip():
            logging.error("Attempted to convert empty text")
            return False

        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{format_type.lower()}') as temp_file:
            temp_path = temp_file.name
            
            try:
                if format_type == 'txt':
                    temp_file.write(text.encode('utf-8'))
                    temp_file.flush()
                    os.fsync(temp_file.fileno())
                elif format_type == 'docx':
                    doc = Document()
                    doc.add_paragraph(text)
                    doc.save(temp_path)
                elif format_type == 'pdf':                    
                    a4_width_mm = 210
                    pt_to_mm = 0.35
                    fontsize_pt = 10
                    fontsize_mm = fontsize_pt * pt_to_mm
                    margin_bottom_mm = 10
                    character_width_mm = 7 * pt_to_mm
                    width_text = a4_width_mm / character_width_mm

                    pdf = FPDF(orientation='P', unit='mm', format='A4')
                    pdf.set_auto_page_break(True, margin=margin_bottom_mm)
                    pdf.add_page()
                    pdf.add_font('DejaVu', '', "app/utils/fonts/DejaVuSerifCondensed.ttf")
                    pdf.set_font("DejaVu", size=fontsize_pt)
                    
                    splitted = text.split('\n')
                    for line in splitted:
                        lines = textwrap.wrap(line, width_text)
                        if len(lines) == 0:
                            pdf.ln()
                        for wrap in lines:
                            pdf.write(fontsize_mm, wrap + '\n')
                    
                    pdf.output(temp_path)
                else:
                    logging.error(f"Unsupported format type: {format_type}")
                    return False
                
                if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                    logging.error("Generated file is empty or does not exist")
                    return False
                
                await bot.send_document(
                    chat_id=user_id,
                    document=FSInputFile(temp_path, filename=f"recognized_text.{format_type.lower()}")
                )
                
                return True
                
            except Exception as e:
                logging.error(f"Error during file conversion: {e}")
                return False
            
    except Exception as e:
        logging.error(f"Error converting and sending text: {e}")
        return False
        
    finally:
        if temp_path and os.path.exists(temp_path):
            for _ in range(3):
                try:
                    os.unlink(temp_path)
                    break
                except Exception as e:
                    logging.error(f"Error cleaning up temporary file (attempt {_ + 1}): {e}")
                    time.sleep(0.5)

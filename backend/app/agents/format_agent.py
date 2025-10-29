"""
Format Agent - Applies final formatting to content
"""
import re


class FormatAgent:
    """
    Formatting specialist that processes markdown content
    No LLM needed - uses text processing
    """
    
    @staticmethod
    def format_chapter(content: str) -> str:
        """
        Format chapter content to ensure proper markdown structure
        
        Args:
            content: Raw chapter content
            
        Returns:
            Formatted markdown content
        """
        # Ensure headings are properly formatted
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Clean up multiple empty lines
            if line.strip() == '':
                if formatted_lines and formatted_lines[-1].strip() != '':
                    formatted_lines.append(line)
                continue
            
            # Ensure proper heading spacing
            if line.startswith('#'):
                if formatted_lines and formatted_lines[-1].strip() != '':
                    formatted_lines.append('')  # Add space before heading
                formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        
        content = '\n'.join(formatted_lines)
        
        # Clean up trailing whitespace
        content = re.sub(r' +\n', '\n', content)
        
        # Ensure proper list formatting
        content = re.sub(r'\n(\d+\.)', r'\n\n\1', content)  # Numbered lists
        content = re.sub(r'\n(-|\*)', r'\n\n\1', content)  # Bullet lists
        
        # Clean up multiple newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content.strip()


import google.generativeai as genai
from pathlib import Path
from config import GEMINI_API_KEY, NOTES_OUTPUT_DIR
import re

__all__ = ['NotesManager']

class NotesManager:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("Gemini API key not configured")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name='gemini-2.0-flash-thinking-exp-01-21',
            generation_config={
                'temperature': 0.7,
                'top_p': 0.9,
                'max_output_tokens': 8000,
            }
        )

    def generate_title(self, transcription):
        try:
            response = self.model.generate_content(
                "Generate a short, descriptive title (max 30 chars, alphanumeric and hyphens only) for this content:\n" + 
                transcription[:1000]
            )
            # Clean and format the title
            title = response.text.strip()
            # Remove quotes, newlines and special characters, keep only alphanumeric and hyphens
            title = re.sub(r'[^a-zA-Z0-9\-]', '', title)
            # Ensure title isn't empty
            return title if title else "untitled-notes"
        except Exception as e:
            print(f"Title generation error: {e}")
            return "untitled-notes"

    def clean_markdown_content(self, content):
        """Clean markdown content to prevent double markdown formatting"""
        # Remove outer markdown code fence if present
        content = re.sub(r'^```markdown\n', '', content)
        content = re.sub(r'\n```$', '', content)
        # Remove any trailing backticks that might remain
        content = content.strip('`')
        return content.strip()

    def generate_notes(self, transcription, original_name):
        try:
            title = self.generate_title(transcription)
            
            prompt = f"""  

                *"Generate structured technical documentation in Markdown format from the provided course video transcript. Follow these guidelines:"*  

                #### **1. Remembering (Basic Recall)**  
                - Start with a **summary** of the key topics covered.  
                - Define important **terms, concepts, and formulas** clearly.  

                #### **2. Understanding (Explain in Own Words)**  
                - Break content into **sections** with clear, hierarchical **headings**.  
                - Rephrase complex ideas in **simpler terms** without losing meaning.  

                #### **3. Applying (Use in Context)**  
                - Provide **real-world examples** or use cases when applicable.  
                - If the content is technical, include **code examples** in proper formatting.  

                #### **4. Analyzing (Break Down into Parts)**  
                - Identify relationships between concepts using **diagrams, lists, or tables**.  
                - Highlight **cause-and-effect relationships** within the topic.  

                #### **5. Evaluating (Critically Assess Information)**  
                - Include potential **limitations, pros & cons, or different viewpoints**.  
                - Add **common mistakes or misconceptions** learners should avoid.  

                #### **6. Creating (Synthesize New Ideas)**  
                - Encourage deeper thinking by suggesting **further questions** for exploration.  
                - Provide possible **next steps for application or advanced learning**.  

                
                - Fix any transcription errors
                - include code if technical
                - mindmaps charts if possible or were a good option to visualize smth
                ---
            Content:
            {transcription}
            """
            
            response = self.model.generate_content(prompt)
            if not response.text:
                raise ValueError("Empty response from model")
            
            # Clean the markdown content
            cleaned_content = self.clean_markdown_content(response.text)
            
            # Create sanitized path
            notes_path = Path(NOTES_OUTPUT_DIR).resolve() / f"{title}.md"
            notes_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content with error handling
            try:
                with open(notes_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {title}\n\n{cleaned_content}")
                return str(notes_path)
            except OSError as e:
                print(f"Failed to write file: {e}")
                raise
                
        except Exception as e:
            print(f"Notes generation error: {e}")
            raise Exception(f"Failed to generate notes: {str(e)}")

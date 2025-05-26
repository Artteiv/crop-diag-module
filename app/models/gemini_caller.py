import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiGenerator:
    def __init__(self, model_name="gemini-2.0-flash", temperature=0):
        self.key = os.environ.get("GEMINI_API_KEY")
        genai.configure(api_key=self.key)

        print(f"{self.key[:4]}...{self.key[-4:]}")

        # Cấu hình generation config
        self.generation_config = {
            "temperature": temperature
        }

        # Hệ thống prompt mặc định
        self.system_prompt = "Bạn là một trợ lý AI hữu ích cho các dự án IT về cây trồng và bệnh cây trồng. Bạn có khả năng trích xuất thông tin từ văn bản được cung cấp và trả dữ liệu bằng tiếng Việt theo yêu cầu."

        # Khởi tạo model
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=self.generation_config,
            system_instruction=self.system_prompt
        )

    def generate(self, prompt="Hello, world!", system_prompt=None):
        # Sử dụng system prompt tùy chỉnh nếu được cung cấp
        if system_prompt:
            model = genai.GenerativeModel(
                model_name=self.model.model_name,
                generation_config=self.generation_config,
                system_instruction=system_prompt
            )
            response = model.generate_content(prompt)
        else:
            response = self.model.generate_content(prompt)
        return response

if __name__ == "__main__":
    generator = GeminiGenerator()

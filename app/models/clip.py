import torch.nn as nn
import torch
import clip
from PIL import Image
# Modify the model to include a classifier for subcategories
class CLIPFineTuner(nn.Module):
    def __init__(self, model, num_classes):
        super(CLIPFineTuner, self).__init__()
        self.model = model
        self.classifier = nn.Linear(model.visual.output_dim, num_classes)

    def forward(self, x):
        with torch.no_grad():
            features = self.model.encode_image(x).float()  # Convert to float32
        return self.classifier(features)

class CLIPModule:
    def __init__(self):
        model, preprocess = clip.load("ViT-B/32", jit=False)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        self.model = CLIPFineTuner(model, 17)


    def predict(model, image_input, classes, transform=None, device='cpu'):
        """
        Dự đoán nhãn cho một ảnh.

        Args:
            model: Mô hình đã huấn luyện (e.g., CLIPFineTuner).
            image_input: Đường dẫn file ảnh (str) hoặc đối tượng PIL.Image.
            classes: Danh sách tên lớp (e.g., dataset.classes).
            transform: Transform để xử lý ảnh (nếu None, phải cung cấp ảnh đã transform).
            device: Thiết bị chạy mô hình ('cuda' hoặc 'cpu').

        Returns:
            str: Nhãn dự đoán (e.g., "cassava_leaf beetle").
        """
        model.eval()
        model = model.to(device)

        # Xử lý ảnh đầu vào
        if isinstance(image_input, str):
            # Đọc ảnh từ đường dẫn
            try:
                image = Image.open(image_input).convert('RGB')
            except Exception as e:
                raise ValueError(f"Không thể mở file ảnh {image_input}: {str(e)}")

            if transform is None:
                raise ValueError("Cần cung cấp transform khi image_input là đường dẫn.")

            image_tensor = transform(image)
        elif isinstance(image_input, Image.Image):
            # Ảnh là PIL.Image
            if transform is None:
                raise ValueError("Cần cung cấp transform khi image_input là PIL.Image.")

            image_tensor = transform(image_input)
        else:
            # Giả định image_input là tensor đã transform
            image_tensor = image_input

        # Đảm bảo tensor có batch dimension
        if image_tensor.dim() == 3:
            image_tensor = image_tensor.unsqueeze(0)

        image_tensor = image_tensor.to(device)

        # Thực hiện suy luận
        with torch.no_grad():
            output = model(image_tensor)
            _, predicted_label_idx = torch.max(output, 1)
            predicted_label = classes[predicted_label_idx.item()]

        return predicted_label


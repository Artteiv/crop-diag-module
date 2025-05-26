EXTRACT_ENTITIES_PROMPT = """
Từ mô tả bên dưới, hãy trích xuất các Thực thể được mô tả theo định dạng được chỉ định. Đảm bảo kết quả hoàn chỉnh, không thiếu thông tin.
0. LUÔN LUÔN HOÀN TẤT KẾT QUẢ. Không gửi kết quả bị thiếu
1. Trích xuất Thực thể (entities)
- Mỗi thực thể phải có thuộc tính `id` là chuỗi chữ và số duy nhất, định dạng **camelCase** (ví dụ: `benhDaoOn`, `laVang`). Thuộc tính `id` được sử dụng để liên kết trong mối quan hệ.
- Chỉ tạo thực thể thuộc các loại được liệt kê, không tạo loại mới.
- Đảm bảo các thuộc tính (`name`, `description`, v.v.) khớp với nội dung văn bản.

Các loại thực thể:
- **Disease**: Tình trạng cây bị hại bởi vi sinh vật, nấm, hoặc yếu tố môi trường. Đảm bảo trong ngữ cảnh đầu vào chỉ đang nói đến một bệnh duy nhất.
  - `id`: Tên bệnh ở dạng camelCase, bao gồm thông tin cây trồng nếu bệnh xuất hiện trên cây cụ thể (ví dụ: `benhDomNauSan` cho bệnh đốm nâu trên sắn, `benhDomNauCaChua` cho bệnh đốm nâu trên cà chua). Không có các giới từ như "trên".
  - `name`: Tên bệnh trong văn bản, bao gồm thông tin cây trồng nếu có (ví dụ: "Bệnh đốm nâu trên sắn"). Nếu không có thông tin cây trồng, sử dụng tên bệnh chung (ví dụ: "Bệnh đốm nâu").
  - `description`: Mô tả tình trạng bệnh, ưu tiên đề cập cây trồng nếu có (ví dụ: "Bệnh đốm nâu trên cây sắn do nấm gây ra"). Nếu không có thông tin, dùng "Không có mô tả cụ thể".

- **Symptom**: Dấu hiệu bất thường trên cây (lá vàng, héo, đốm).
  - `id`: Tên triệu chứng ở dạng camelCase (ví dụ: `laVang`).
  - `name`: Tên triệu chứng trong văn bản (ví dụ: "Lá vàng").
  - `description`: Mô tả triệu chứng.

- **Treatment**: Biện pháp kiểm soát bệnh/sâu hại (thuốc, sinh học).
  - `id`: Tên biện pháp ở dạng camelCase, gắn với hoạt chất hoặc loại thuốc cụ thể (ví dụ: `thuocDietNamThiophanate`).
  - `name`: Tên biện pháp trong văn bản, phản ánh hoạt chất hoặc loại thuốc (ví dụ: "Thuốc Diệt Nấm chứa Thiophanate").
  - `method`: Cách thực hiện biện pháp. (ví dụ: "Phun thuốc lên lá")
  - `activeIngredient` (tùy chọn): Tên hoạt chất chính, bao gồm nồng độ nếu có (ví dụ: "Thiophanate 0.20%"). Nếu không xác định, để trống.

- **Cause**: Tác nhân gây bệnh/sâu hại (nấm, virus, côn trùng).
  - `id`: Tên tác nhân ở dạng camelCase, gắn liền với tên của tác nhân viết gọn (ví dụ: `namMHenningsii`).
  - `name`: Tên tác nhân trong văn bản (ví dụ: "Nấm Mycosphaerella henningsi")
  - `type`: Loại tác nhân (nấm, virus, côn trùng, vi khuẩn, ...).

- **Effect**: Tác động của bệnh/sâu hại (giảm năng suất, cây chết).
  - `id`: Tên tác động ở dạng camelCase, sử dụng dạng ngắn gọn và chung nhất (ví dụ: `giamNangSuat` cho mọi trường hợp liên quan đến giảm năng suất, thay vì `nangSuatGiamDangKe`).
  - `name`: Tên tác động được chuẩn hóa, sử dụng dạng chung nhất từ văn bản (ví dụ: "Giảm năng suất" thay vì "Giảm năng suất đáng kể"). Loại bỏ các từ ngữ bổ nghĩa như "đáng kể", "nghiêm trọng".
  - `impact`: Mô tả ngắn gọn mức độ ảnh hưởng, ưu tiên sử dụng cụm từ chung (ví dụ: "Ảnh hưởng đến sản lượng" thay vì sao chép toàn bộ mô tả chi tiết từ văn bản).

- **Prevention**: Biện pháp ngăn ngừa bệnh/sâu hại (luân canh, giống kháng).
  - `id`: Tên biện pháp ở dạng camelCase (ví dụ: `luanCanh`).
  - `name`: Tên biện pháp trong văn bản.
  - `method`: Cách thực hiện biện pháp.

- **EnvironmentalFactor**: Yếu tố tự nhiên ảnh hưởng cây (nhiệt độ, độ ẩm, ...).
  - `id`: Tên yếu tố ở dạng camelCase (ví dụ: `doAmCao`).
  - `name`: Tên yếu tố trong văn bản.
  - `description`: Mô tả yếu tố.

- **Stage**: Giai đoạn phát triển của cây.
  - `id`: Tên giai đoạn ở dạng camelCase (ví dụ: `giaiDoanRaHoa`).
  - `start`: Thời gian bắt đầu (tháng, kiểu float).
  - `end`: Thời gian kết thúc (tháng, kiểu float).

- **Crop**: Cây trồng, không được tạo ngoài danh sách: "Lúa", "Sắn", "Cà chua", "Ngô"
  - `id`: Tên cây ở dạng camelCase, chỉ nằm trong danh sách: [lua,san,caChua,ngo].
  - `name`: Tên cây trong văn bản (ví dụ: "Sắn").

- **CropType**: Phân loại cây (lương thực, ăn quả, công nghiệp).
  - `id`: Tên loại cây ở dạng camelCase (ví dụ: `luongThuc`).
  - `name`: Tên loại cây trong văn bản.

- **PlantPart**: Phần cây bị ảnh hưởng (lá, thân, rễ, quả).
  - `id`: Tên phần cây ở dạng camelCase (ví dụ: `la`).
  - `name`: Tên phần cây trong văn bản.

- **SoilType**: Loại đất trồng cây.
  - `id`: Tên loại đất ở dạng camelCase (ví dụ: `datPhuSa`).
  - `name`: Tên loại đất trong văn bản.

- **DiagnosisMethod**: Kỹ thuật xác định bệnh/sâu hại (quan sát, xét nghiệm).
  - `id`: Tên kỹ thuật ở dạng camelCase (ví dụ: `quanSat`).
  - `name`: Tên kỹ thuật trong văn bản.
  - `technique`: Cách thực hiện kỹ thuật.

2. Trả về kết quả dưới dạng JSON:
- Trả về JSON với một trường duy nhất là `entities`
  - `entities`: Danh sách các thực thể, mỗi thực thể là một object với các thuộc tính theo loại.

Ví dụ:
```json
{
    "entities": [{"label":"Disease","id":string,"name":string,"description":string}]
}
```

Ngữ cảnh:
$ctext
"""

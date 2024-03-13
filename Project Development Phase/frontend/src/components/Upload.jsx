import { useState } from "react";
import "../index.css";
import Result from "./Result";

const ImageCaptionGenerator = () => {
  const [selectedFile, setSelectedFile] = useState("");
  const [bool, setBool] = useState(false);

  const handleImageChange = (event) => {
    const img = event.target.files[0];
    setSelectedFile(img);
  };

  const handleGenerateCaption = () => {
    if (selectedFile) setBool(true);
    else {
      window.alert("Select image first");
    }
  };

  return (
    <>
      <div>
        {!bool && (
          <>
            <input
              type="file"
              style={{ color: "black" }}
              onChange={handleImageChange}
            />
            <div>
              <button onClick={handleGenerateCaption}>Generate Caption</button>
            </div>
          </>
        )}

        {bool && <Result img={selectedFile} />}
      </div>
    </>
  );
};

export default ImageCaptionGenerator;

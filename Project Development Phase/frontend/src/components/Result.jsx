import { useEffect, useState } from "react";
import Loader from "./Loader";
import Upload from "./Upload";

const Result = (props) => {
  const [preview, setPreview] = useState();
  const [caption, setCaption] = useState(); // Changing caption on UI
  const [bool1, setBool] = useState(false);

  const fetchCaption = async () => {
    const formData = new FormData();
    formData.append("file", props.img);

    try {
      const url = `http://localhost:9090/generate`;
      const response = await fetch(url, {
        method: "Post",
        body: formData,
      });

      const data = await response.json();
      setCaption(data.caption);
    } catch (err) {
      console.log(err);
    }
  };
  useEffect(() => {
    setPreview(URL.createObjectURL(props.img));

    fetchCaption();
  }, []);

  const handleClick = () => {
    setBool(true);
  };

  return (
    <>
      {!bool1 && (
        <div className="result-page">
          <div className="result-window" style={{ position: "reative" }}>
            <button
              style={{ color: "black", marginLeft: "-31rem" }}
              className="result-logout"
              onClick={handleClick}
            >
              Go back
            </button>
            <h1 className="result-heading">Result page</h1>
            {preview && (
              <img className="result-image" src={preview} alt="image" />
            )}
            {caption ? <p className="result-caption">{caption}</p> : <Loader />}
          </div>
        </div>
      )}

      {bool1 && <Upload />}
    </>
  );
};

export default Result;

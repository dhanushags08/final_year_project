import { BrowserRouter, Routes, Route } from "react-router-dom";
import VideoPlayer from "./pages/main";
import { Detect } from "./pages/detect";
import { RecoilRoot } from "recoil";
import Numberplate from "./pages/forNumberPlate";
import { Image } from "./pages/image";
function App() {
  return (
    <>
      <BrowserRouter>
        <RecoilRoot>
          <Routes>
            <Route path="/" element={<VideoPlayer />} />
            <Route path="/detect" element={<Detect />} />
            <Route path="/numberplate" element={<Numberplate />} />
            <Route path="/image" element={<Image />} />
          </Routes>
        </RecoilRoot>
      </BrowserRouter>
    </>
  );
}

export default App;

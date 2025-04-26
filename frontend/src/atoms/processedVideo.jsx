import { atom } from "recoil";

export const fileState = atom({ key: "fileState", default: null });
export const processedVideoState = atom({
  key: "processedVideoState",
  default: null,
});
export const imageState = atom({ key: "imageState", default: null });
export const processedImageState = atom({
  key: "processedImageState",
  default: null,
});

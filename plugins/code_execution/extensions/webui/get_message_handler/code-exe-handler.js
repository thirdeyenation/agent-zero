import { drawMessageCodeExe } from "/js/messages.js";

export default async function registerCodeExeHandler(extData) {
  if (extData?.type === "code_exe") {
    extData.handler = drawMessageCodeExe;
  }
}

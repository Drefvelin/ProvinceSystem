import { renderPreviewJob, type RenderJob } from "./scene";

declare global {
  interface Window {
    renderPreviewJob: (job: RenderJob) => Promise<Record<string, string>>;
  }
}

window.renderPreviewJob = renderPreviewJob;

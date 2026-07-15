import api from "../api/axios";

/**
 * Downloads a file from an authenticated API endpoint.
 * Plain <a href="/api/..."> links don't carry the JWT token, so exports
 * must be fetched via axios (which attaches Authorization) and then
 * saved as a Blob.
 */
export async function downloadExport(genId, format, suggestedName) {
  const res = await api.get(`/export/${genId}/${format}`, {
    responseType: "blob",
  });

  const blob = new Blob([res.data]);
  const url = window.URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = suggestedName || `export_${genId}.${format === "docx" ? "docx" : "pdf"}`;
  document.body.appendChild(a);
  a.click();
  a.remove();

  window.URL.revokeObjectURL(url);
}

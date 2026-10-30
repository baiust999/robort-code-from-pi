/** Hands `blob` to the browser as a download named `filename`. */
export function download(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  // Revoked later: some browsers read the blob after click() returns.
  setTimeout(() => URL.revokeObjectURL(url), 10_000);
}

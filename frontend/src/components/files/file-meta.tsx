export function FileMeta({ file }: any) {
  return <div className="space-y-2 text-sm">
    <div>Size: {file.file_size} bytes</div>
    <div>Type: {file.mime_type}</div>
  </div>;
}

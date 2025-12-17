export function FilePreview({ file }: any) {
  return <div className="aspect-video bg-gray-100 flex items-center justify-center">
    Preview: {file.final_filename}
  </div>;
}

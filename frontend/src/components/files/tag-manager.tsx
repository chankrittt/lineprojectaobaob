export function TagManager({ fileId, tags }: any) {
  return <div className="flex flex-wrap gap-2">
    {tags.map((tag: string) => (
      <span key={tag} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
        #{tag}
      </span>
    ))}
  </div>;
}

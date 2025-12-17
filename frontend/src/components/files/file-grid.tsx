export function FileGrid({ searchQuery }: { searchQuery: string }) {
  return <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
    <div className="border rounded-lg p-4">File Grid - {searchQuery}</div>
  </div>;
}

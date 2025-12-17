export function StorageStats({ stats }: any) {
  return <div>Storage: {stats?.total_size || 0} bytes</div>;
}

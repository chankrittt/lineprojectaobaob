import { Button } from "./button";

export function ViewToggle({ view, onViewChange, options }: any) {
  return (
    <div className="flex gap-1">
      {options.map((opt: any) => (
        <Button
          key={opt.value}
          variant={view === opt.value ? "default" : "outline"}
          size="icon"
          onClick={() => onViewChange(opt.value)}
        >
          <opt.icon className="w-4 h-4" />
        </Button>
      ))}
    </div>
  );
}

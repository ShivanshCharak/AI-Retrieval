export default function OrbIcon() {
  return (
    <div className="w-28 h-28 rounded-full overflow-hidden relative shrink-0">
      <div
        className="absolute inset-0 rounded-full"
        style={{
          background:
            "radial-gradient(circle at 40% 35%, #f8b4a0 0%, #e8a0c0 30%, #c4a8e0 60%, #b8c8f0 100%)",
          filter: "blur(8px)",
          transform: "scale(0.95)",
        }}
      />
      <div
        className="absolute inset-0 rounded-full"
        style={{
          background:
            "radial-gradient(circle at 55% 30%, rgba(255,255,255,0.35) 0%, transparent 55%)",
        }}
      />
    </div>
  );
}

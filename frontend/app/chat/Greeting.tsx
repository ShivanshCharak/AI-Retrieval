interface GreetingProps {
  name: string;
}

export default function Greeting({ name }: GreetingProps) {
  return (
    <div className="text-center">
      <h1 className="text-3xl font-bold text-gray-900 mb-1">Good Morning, {name}</h1>
      <p className="text-3xl font-bold text-gray-900">
        How Can I{" "}
        <span className="text-purple-400">Assist You Today?</span>
      </p>
    </div>
  );
}

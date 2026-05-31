interface MetricCardProps {
  title: string;
  value: string;
}

export default function MetricCard({ title, value }: MetricCardProps) {
  return (
    <div className="group relative rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-all duration-200 hover:border-gray-300 hover:shadow-md hover:-translate-y-0.5">
      {/* Subtle top highlight for depth */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent opacity-60" />
      
      <div className="flex flex-col gap-1.5">
        <p className="text-sm font-medium tracking-wide text-gray-500">
          {title}
        </p>
        
        <h3 className="text-2xl font-bold tracking-tight text-gray-900 sm:text-3xl">
          {value}
        </h3>
      </div>

      {/* Hover accent line */}
      <div className="absolute bottom-0 left-0 h-0.5 w-0 bg-blue-500 transition-all duration-300 group-hover:w-full" />
    </div>
  );
}
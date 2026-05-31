"use client";

import { useEffect, useState } from "react";

import MetricCard from "@/app/src/components/MetricCard";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  BarChart,
  Bar,
} from "recharts";

export default function Home() {
  const [data, setData] = useState<any>(null);

useEffect(() => {
  fetch("/report.json")
    .then((res) => res.json())
    .then((json) => setData(json))
    .catch((err) => console.error(err));
}, []);
if (!data) {
  return (
    <main className="min-h-screen flex items-center justify-center">
      <p>Loading analytics...</p>
    </main>
  );
}

  return (
    <main className="min-h-screen bg-gray-50/50 p-6 md:p-10">
      <div className="mx-auto max-w-7xl space-y-8">
        
        {/* HEADER */}
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-gray-900 md:text-4xl">
              Delivery Operations Copilot
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Real-time performance monitoring & optimization insights
            </p>
          </div>
          <span className="inline-flex items-center rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 ring-1 ring-inset ring-emerald-600/20 sm:self-center">
            <span className="mr-1.5 h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Live Data
          </span>
        </div>

        {/* KPI CARDS */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard title="Orders" value={data.kpis.orders.toLocaleString()} />
          <MetricCard title="Revenue" value={`€${data.kpis.revenue.toLocaleString()}`} />
          <MetricCard title="Avg Delivery" value={`${data.kpis.avgDelivery} min`} />
          <MetricCard title="Late Deliveries" value={`${data.kpis.lateRate}%`} />
        </div>

        {/* CHARTS GRID */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <SectionCard title="Delivery Time Trend">
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.trend}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                  <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: "#6b7280", fontSize: 12 }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: "#6b7280", fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#fff", border: "1px solid #e5e7eb", borderRadius: "8px", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
                    labelStyle={{ fontWeight: 600, marginBottom: 4, color: "#111827" }}
                  />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#3b82f6"
                    strokeWidth={2.5}
                    dot={false}
                    activeDot={{ r: 5, stroke: "#3b82f6", strokeWidth: 2, fill: "#fff" }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </SectionCard>

          <SectionCard title="Zone Performance">
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.zones}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                  <XAxis dataKey="zone" axisLine={false} tickLine={false} tick={{ fill: "#6b7280", fontSize: 12 }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: "#6b7280", fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#fff", border: "1px solid #e5e7eb", borderRadius: "8px", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
                    cursor={{ fill: "#f3f4f6" }}
                  />
                  <Bar dataKey="deliveryTime" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </SectionCard>
        </div>

        {/* BOTTOM SECTION: TABLE & ROOT CAUSE */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          
          {/* RESTAURANTS TABLE */}
          <SectionCard title="Restaurant Bottlenecks" className="lg:col-span-2">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-gray-200 text-xs font-medium uppercase tracking-wider text-gray-500">
                    <th className="pb-3">Restaurant</th>
                    <th className="pb-3 text-right">Avg Prep Time</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {data.restaurants.map((restaurant) => (
                    <tr key={restaurant.name} className="group hover:bg-gray-50 transition-colors">
                      <td className="py-3 font-medium text-gray-900 group-hover:text-gray-700">
                        {restaurant.name}
                      </td>
                      <td className="py-3 text-right text-gray-600 tabular-nums">
                        {restaurant.prepTime} min
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </SectionCard>

          {/* ROOT CAUSE ANALYSIS */}
          <SectionCard title="Root Cause Analysis" className="lg:col-span-1">
            <div className="space-y-4">
              <div className="rounded-lg bg-blue-50 p-4 ring-1 ring-inset ring-blue-700/10">
                <h3 className="text-sm font-semibold text-blue-800">Primary Cause</h3>
                <p className="mt-1 text-sm text-blue-700 leading-relaxed">
                  {data.rootCause.cause}
                </p>
              </div>
              <div className="rounded-lg bg-gray-50 p-4 ring-1 ring-inset ring-gray-200">
                <h3 className="text-sm font-semibold text-gray-800">Recommendation</h3>
                <p className="mt-1 text-sm text-gray-600 leading-relaxed">
                  {data.rootCause.recommendation}
                </p>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-500 pt-1">
                <svg className="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>AI-generated insight based on current metrics</span>
              </div>
            </div>
          </SectionCard>

        </div>
      </div>
    </main>
  );
}

// Reusable card wrapper for consistent section styling
function SectionCard({
  title,
  children,
  className = "",
}: {
  title: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`rounded-xl border border-gray-200 bg-white p-6 shadow-sm ${className}`}>
      <h2 className="mb-4 text-lg font-semibold text-gray-900">{title}</h2>
      {children}
    </div>
  );
}
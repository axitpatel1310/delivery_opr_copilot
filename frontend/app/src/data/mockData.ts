export const dashboardData = {
  kpis: {
    orders: 1000000,
    revenue: 34891122,
    avgDelivery: 32.8,
    lateRate: 11.4,
  },

  trend: [
    { day: "Mon", value: 28 },
    { day: "Tue", value: 30 },
    { day: "Wed", value: 33 },
    { day: "Thu", value: 31 },
    { day: "Fri", value: 38 },
    { day: "Sat", value: 40 },
    { day: "Sun", value: 35 },
  ],

  zones: [
    { zone: "Mitte", deliveryTime: 36 },
    { zone: "Kreuzberg", deliveryTime: 34 },
    { zone: "Neukölln", deliveryTime: 32 },
    { zone: "Charlottenburg", deliveryTime: 29 },
  ],

  restaurants: [
    { name: "Restaurant_44", prepTime: 24 },
    { name: "Restaurant_11", prepTime: 22 },
    { name: "Restaurant_72", prepTime: 21 },
    { name: "Restaurant_08", prepTime: 20 },
    { name: "Restaurant_55", prepTime: 19 },
  ],

  rootCause: {
    cause: "Restaurant Delays",
    recommendation:
      "Investigate Restaurant_44 preparation bottlenecks.",
  },
};
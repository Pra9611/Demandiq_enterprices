import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import {
  Home,
  LineChart,
  AlertTriangle,
  Activity,
  RefreshCw,
  BarChart3,
  ShieldCheck,
  IndianRupee,
  Package,
} from "lucide-react";
import "./style.css";

const API = "http://127.0.0.1:8000";

const formatNumber = (num) =>
  new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 }).format(num || 0);

const formatCurrency = (num) =>
  "₹" +
  new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 }).format(num || 0);

function StatCard({ title, value, subtitle, icon: Icon, type }) {
  return (
    <div className={`statCard ${type}`}>
      <div>
        <p>{title}</p>
        <h2>{value}</h2>
        <span>{subtitle}</span>
      </div>
      <div className="iconBox">
        <Icon size={30} />
      </div>
    </div>
  );
}

function App() {
  const [summary, setSummary] = useState({});
  const [chartData, setChartData] = useState([]);
  const [activePage, setActivePage] = useState("Dashboard");
  const [timeFilter, setTimeFilter] = useState("Monthly");
  const [monitorFilter, setMonitorFilter] = useState("revenue");

  const [analysis, setAnalysis] = useState({
    top_products: [],
    stock_risk: [],
    revenue_trend: [],
  });

  useEffect(() => {
    fetch(`${API}/api/forecast/summary`)
      .then((res) => res.json())
      .then((data) => {
        setSummary(data || {});
        setChartData(data?.forecast_data || []);
      })
      .catch((err) => console.error("Summary API Error:", err));

    fetch(`${API}/api/forecast/analysis`)
      .then((res) => res.json())
      .then((data) => {
        setAnalysis(
          data || {
            top_products: [],
            stock_risk: [],
            revenue_trend: [],
          }
        );
      })
      .catch((err) => console.error("Analysis API Error:", err));
  }, []);

  let filteredForecast = chartData;

  if (timeFilter === "Weekly") {
    filteredForecast = chartData.slice(0, 7);
  }

  if (timeFilter === "Monthly") {
    filteredForecast = chartData.slice(0, 30);
  }

  if (timeFilter === "Quarterly") {
    filteredForecast = chartData.slice(0, 90);
  }

  if (timeFilter === "Yearly") {
    filteredForecast = chartData.slice(0, 365);
  }

  const confidenceData = [
    { name: "confidence", value: summary.confidence || 0 },
    { name: "remaining", value: 100 - (summary.confidence || 0) },
  ];

  const menu = [
    { name: "Dashboard", icon: Home },
    { name: "Forecasts", icon: LineChart },
    { name: "Stock Risk", icon: AlertTriangle },
    { name: "Monitoring", icon: Activity },
    { name: "Retraining", icon: RefreshCw },
  ];

  return (
    <main className="app">
      <aside className="sidebar">
        <div className="brand">
          <BarChart3 size={34} />
          <div>
            <h1>DemandIQ</h1>
            <p>Enterprise Forecasting</p>
          </div>
        </div>

        <nav>
          {menu.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.name}
                className={activePage === item.name ? "navBtn active" : "navBtn"}
                onClick={() => setActivePage(item.name)}
              >
                <Icon size={21} />
                {item.name}
              </button>
            );
          })}
        </nav>

        <div className="confidenceBox">
          <p>Model Confidence</p>
          <div className="donutWrap">
            <PieChart width={150} height={150}>
              <Pie
                data={confidenceData}
                innerRadius={54}
                outerRadius={68}
                dataKey="value"
                startAngle={90}
                endAngle={-270}
              >
                <Cell fill="#10b981" />
                <Cell fill="#12314f" />
              </Pie>
            </PieChart>

            <div className="donutText">
              <h2>{summary.confidence || 0}%</h2>
              <span>High</span>
            </div>
          </div>
          <small>Last updated: Live</small>
        </div>
      </aside>

      <section className="content">
        <div className="topbar">
          <div>
            <h1>{activePage}</h1>
            <p>Multi-horizon forecasting, stockout risk and model monitoring.</p>
          </div>

          <div className="timeBox">
            <span>Live Dataset</span>
            <b>{timeFilter}</b>
          </div>
        </div>

        {activePage === "Dashboard" && (
          <>
            <div className="cards">
              <StatCard
                title="Forecast Units"
                value={formatNumber(summary.total_forecast_units)}
                subtitle="Total forecasted units"
                icon={Package}
                type="blue"
              />

              <StatCard
                title="Revenue Forecast"
                value={formatCurrency(summary.revenue_forecast)}
                subtitle="Total forecasted revenue"
                icon={IndianRupee}
                type="green"
              />

              <StatCard
                title="Stockout Risks"
                value={formatNumber(summary.stockout_risk_products)}
                subtitle="Products at risk"
                icon={AlertTriangle}
                type="orange"
              />

              <StatCard
                title="Model Confidence"
                value={`${summary.confidence || 0}%`}
                subtitle="Dynamic confidence"
                icon={ShieldCheck}
                type="purple"
              />
            </div>

            <div className="chartBox large">
              <div className="chartHead">
                <h2>{timeFilter} Product Forecast</h2>

                <select
                  className="filterSelect"
                  value={timeFilter}
                  onChange={(e) => setTimeFilter(e.target.value)}
                >
                  <option value="Weekly">Weekly - 7 Days</option>
                  <option value="Monthly">Monthly - 30 Days</option>
                  <option value="Quarterly">Quarterly - 90 Days</option>
                  <option value="Yearly">Yearly - 365 Days</option>
                </select>
              </div>

              <ResponsiveContainer width="100%" height={340}>
                <AreaChart data={filteredForecast}>
                  <defs>
                    <linearGradient id="blueArea" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.55} />
                      <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0.04} />
                    </linearGradient>
                  </defs>

                  <CartesianGrid strokeDasharray="4 4" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip />

                  <Area
                    type="monotone"
                    dataKey="demand"
                    stroke="#0ea5e9"
                    fill="url(#blueArea)"
                    strokeWidth={4}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div className="twoGrid">
              <div className="chartBox">
                <div className="chartHead">
                  <h2>Top Demand Products</h2>
                  <button onClick={() => setActivePage("Forecasts")}>View All</button>
                </div>

                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={analysis?.top_products || []}>
                    <CartesianGrid strokeDasharray="4 4" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="demand" fill="#0ea5e9" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="chartBox">
                <div className="chartHead">
                  <h2>Demand Trend</h2>
                  <button onClick={() => setActivePage("Monitoring")}>View All</button>
                </div>

                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={filteredForecast}>
                    <CartesianGrid strokeDasharray="4 4" />
                    <XAxis dataKey="day" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="demand" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </>
        )}

        {activePage === "Forecasts" && (
          <div className="chartBox large">
            <h2>Top Demand Products</h2>

            <ResponsiveContainer width="100%" height={430}>
              <BarChart data={analysis?.top_products || []}>
                <CartesianGrid strokeDasharray="4 4" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="demand" fill="#0ea5e9" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {activePage === "Stock Risk" && (
          <div className="chartBox large">
            <h2>Stock Risk Products</h2>

            <ResponsiveContainer width="100%" height={430}>
              <BarChart data={analysis?.stock_risk || []}>
                <CartesianGrid strokeDasharray="4 4" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="risk_score" fill="#f59e0b" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {activePage === "Monitoring" && (
          <>
            <div className="chartFilters">
              <select
                value={monitorFilter}
                onChange={(e) => setMonitorFilter(e.target.value)}
                className="filterSelect"
              >
                <option value="revenue">Revenue Trend</option>
                <option value="region">Region Revenue</option>
                <option value="category">Category Revenue</option>
                <option value="store">Store Revenue</option>
              </select>
            </div>

            <div className="chartBox large">
              <h2>
                {monitorFilter === "revenue" && "Revenue Monitoring"}
                {monitorFilter === "region" && "Revenue by Region"}
                {monitorFilter === "category" && "Revenue by Category"}
                {monitorFilter === "store" && "Revenue by Store"}
              </h2>

              <ResponsiveContainer width="100%" height={430}>
                {monitorFilter === "category" ? (
                  <PieChart>
                    <Pie
                      data={analysis?.category_revenue || []}
                      dataKey="revenue"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      innerRadius={90}
                      outerRadius={150}
                      paddingAngle={4}
                      label = {({ name, value }) =>
                          `${name}: ₹${(value / 10000000).toFixed(1)}Cr`}
                    >
                      {(analysis?.category_revenue || []).map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={
                            ["#8b5cf6", "#0ea5e9", "#10b981", "#f59e0b", "#ef4444"][
                              index % 5
                            ]
                          }
                        />
                      ))}
                    </Pie>

                    <Tooltip
                      formatter={(value) => [`₹${formatNumber(value)}`, "Revenue"]}
                    />
                  </PieChart>
                ) : monitorFilter === "revenue" ? (
                  <AreaChart data={analysis?.revenue_trend || []}>
                    <CartesianGrid strokeDasharray="4 4" />
                    <XAxis dataKey="name" />
                    <YAxis
                      tickFormatter={(value) =>
                        `${(value / 10000000).toFixed(1)}Cr`
                      }
                    />
                    <Tooltip
                      formatter={(value, name) => [`₹${formatNumber(value)}`, "Revenue"]}
                    />
                    <Area
                      type="monotone"
                      dataKey="revenue"
                      stroke="#22c55e"
                      fill="#22c55e55"
                      strokeWidth={4}
                    />
                  </AreaChart>
                ) : (
                  <BarChart
                    data={
                      monitorFilter === "region"
                        ? analysis?.region_revenue || []
                        : analysis?.store_revenue || []
                    }
                  >
                    <CartesianGrid strokeDasharray="4 4" />
                    <XAxis dataKey="name" />
                    <YAxis
                      tickFormatter={(value) =>
                        `${(value / 10000000).toFixed(1)}Cr`
                      }
                    />
                    <Tooltip
                      formatter={(value) => [`₹${formatNumber(value)}`, "Revenue"]}
                    />
                    <Bar
                      dataKey="revenue"
                      fill={monitorFilter === "region" ? "#0ea5e9" : "#f59e0b"}
                      radius={[8, 8, 0, 0]}
                    />
                  </BarChart>
                )}
              </ResponsiveContainer>
            </div>
          </>
        )}

        {activePage === "Retraining" && (
          <div className="chartBox large">
            <h2>Model Retraining Status</h2>

            <div className="retrainGrid">
              <StatCard
                title="Current Confidence"
                value={`${summary.confidence || 0}%`}
                subtitle="Model health score"
                icon={ShieldCheck}
                type="purple"
              />

              <StatCard
                title="Training Data"
                value={formatNumber(summary.total_forecast_units)}
                subtitle="Rows analyzed"
                icon={Package}
                type="blue"
              />

              <StatCard
                title="Risk Samples"
                value={formatNumber(summary.stockout_risk_products)}
                subtitle="High-risk signals"
                icon={AlertTriangle}
                type="orange"
              />
            </div>
          </div>
        )}
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
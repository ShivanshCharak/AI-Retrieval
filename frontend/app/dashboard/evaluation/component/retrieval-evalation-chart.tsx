"use client"

import React from "react"

import {
  CartesianGrid,
  Line,
  LineChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  type ChartConfig,
} from "@/components/ui/chart"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

// =========================================================
// TYPES
// =========================================================

type EvalRow = {
  id: number
  query: string
  expected_id: string
  rank: number | null

  "recall@1": number
  "recall@3": number
  "recall@5": number
  "recall@10": number

  "hit_rate@1": number
  "hit_rate@3": number
  "hit_rate@5": number
  "hit_rate@10": number

  "ndcg@1": number
  "ndcg@3": number
  "ndcg@5": number
  "ndcg@10": number

  mrr: number
  passed: boolean
}

type EvaluationRun = {
  file: string
  count: number
  rows: EvalRow[]
}

type EvaluationResponse = {
  dense: EvaluationRun
  hybrid: EvaluationRun
  reranked: EvaluationRun
}

type ChartData = {
  k: string
  dense: number
  hybrid: number
  reranked: number
}

// =========================================================
// CHART CONFIG
// =========================================================

const chartConfig = {
  dense: {
    label: "Dense",
    color: "#2563EB",
  },

  hybrid: {
    label: "Hybrid",
    color: "#A855F7",
  },

  reranked: {
    label: "Reranked",
    color: "#22C55E",
  },
} satisfies ChartConfig

// =========================================================
// AVERAGE
// =========================================================

function average(
  rows: EvalRow[],
  key: keyof EvalRow,
): number {
  if (!rows.length) {
    return 0
  }

  return (
    rows.reduce(
      (sum, row) =>
        sum + Number(row[key] ?? 0),
      0,
    ) / rows.length
  )
}

// =========================================================
// FIND BEST VALUE
// =========================================================

function getBestMetric(
  evaluation: EvaluationResponse,
  metric: keyof EvalRow,
) {
  const runs = [
    {
      name: "Dense",
      key: "dense" as const,
      run: evaluation.dense,
    },
    {
      name: "Hybrid",
      key: "hybrid" as const,
      run: evaluation.hybrid,
    },
    {
      name: "Reranked",
      key: "reranked" as const,
      run: evaluation.reranked,
    },
  ]

  const results = runs.map((item) => ({
    name: item.name,
    key: item.key,
    value: average(item.run.rows, metric),
  }))

  return results.reduce((best, current) =>
    current.value > best.value
      ? current
      : best,
  )
}

// =========================================================
// CUSTOM TOOLTIP
// =========================================================

function RetrievalTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean
  payload?: any[]
  label?: string
}) {
  if (
    !active ||
    !payload ||
    payload.length === 0
  ) {
    return null
  }

  const sortedPayload = [...payload].sort(
    (a, b) =>
      Number(b.value ?? 0) -
      Number(a.value ?? 0),
  )

  return (
    <div className="rounded-lg border bg-background p-3 shadow-xl">
      <p className="mb-2 text-sm font-semibold">
        {label}
      </p>

      <div className="space-y-2">
        {sortedPayload.map((entry) => {
          const key =
            entry.dataKey as keyof typeof chartConfig

          const config = chartConfig[key]

          return (
            <div
              key={String(entry.dataKey)}
              className="flex items-center justify-between gap-8"
            >
              <div className="flex items-center gap-2">
                <span
                  className="h-2.5 w-2.5 rounded-full"
                  style={{
                    backgroundColor:
                      config?.color,
                  }}
                />

                <span className="text-sm text-muted-foreground">
                  {config?.label ??
                    String(entry.dataKey)}
                </span>
              </div>

              <span className="font-mono text-sm font-semibold">
                {Number(
                  entry.value ?? 0,
                ).toFixed(1)}
                %
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// =========================================================
// COMPONENT
// =========================================================

export function RetrievalEvaluationChart() {
  const [chartData, setChartData] =
    React.useState<ChartData[]>([])

  const [evaluation, setEvaluation] =
    React.useState<EvaluationResponse | null>(
      null,
    )

  const [loading, setLoading] =
    React.useState(true)

  const [error, setError] =
    React.useState<string | null>(null)

  // =======================================================
  // FETCH
  // =======================================================

  React.useEffect(() => {
    async function loadEvaluationData() {
      try {
        setLoading(true)
        setError(null)

        const response = await fetch(
          "http://localhost:8000/api/v1/evaluation/retrieval",
        )

        if (!response.ok) {
          throw new Error(
            "Failed to load retrieval evaluation.",
          )
        }

        const data: EvaluationResponse =
          await response.json()

        setEvaluation(data)

        const denseRows =
          data.dense.rows

        const hybridRows =
          data.hybrid.rows

        const rerankedRows =
          data.reranked.rows

        setChartData([
          {
            k: "@1",

            dense:
              average(
                denseRows,
                "recall@1",
              ) * 100,

            hybrid:
              average(
                hybridRows,
                "recall@1",
              ) * 100,

            reranked:
              average(
                rerankedRows,
                "recall@1",
              ) * 100,
          },

          {
            k: "@3",

            dense:
              average(
                denseRows,
                "recall@3",
              ) * 100,

            hybrid:
              average(
                hybridRows,
                "recall@3",
              ) * 100,

            reranked:
              average(
                rerankedRows,
                "recall@3",
              ) * 100,
          },

          {
            k: "@5",

            dense:
              average(
                denseRows,
                "recall@5",
              ) * 100,

            hybrid:
              average(
                hybridRows,
                "recall@5",
              ) * 100,

            reranked:
              average(
                rerankedRows,
                "recall@5",
              ) * 100,
          },

          {
            k: "@10",

            dense:
              average(
                denseRows,
                "recall@10",
              ) * 100,

            hybrid:
              average(
                hybridRows,
                "recall@10",
              ) * 100,

            reranked:
              average(
                rerankedRows,
                "recall@10",
              ) * 100,
          },
        ])
      } catch (err) {
        console.error(
          "Failed to load retrieval evaluation:",
          err,
        )

        setError(
          err instanceof Error
            ? err.message
            : "Failed to load evaluation data.",
        )
      } finally {
        setLoading(false)
      }
    }

    loadEvaluationData()
  }, [])

  // =======================================================
  // LOADING
  // =======================================================

  if (loading) {
    return (
      <Card className="h-[500px] w-full">
        <CardHeader>
          <CardTitle>
            Retrieval Quality
          </CardTitle>

          <CardDescription>
            Recall@K comparison — Dense vs Hybrid
            vs Reranked
          </CardDescription>
        </CardHeader>

        <CardContent className="flex h-[400px] items-center justify-center">
          <p className="text-sm text-muted-foreground">
            Loading evaluation data...
          </p>
        </CardContent>
      </Card>
    )
  }

  // =======================================================
  // ERROR
  // =======================================================

  if (error) {
    return (
      <Card className="h-[500px] w-full">
        <CardHeader>
          <CardTitle>
            Retrieval Quality
          </CardTitle>
        </CardHeader>

        <CardContent className="flex h-[400px] items-center justify-center">
          <p className="text-sm text-destructive">
            {error}
          </p>
        </CardContent>
      </Card>
    )
  }

  // =======================================================
  // NO DATA
  // =======================================================

  if (!evaluation) {
    return (
      <Card className="h-[500px] w-full">
        <CardHeader>
          <CardTitle>
            Retrieval Quality
          </CardTitle>
        </CardHeader>

        <CardContent className="flex h-[400px] items-center justify-center">
          <p className="text-sm text-muted-foreground">
            No evaluation data available.
          </p>
        </CardContent>
      </Card>
    )
  }

  // =======================================================
  // BEST METRICS
  // =======================================================

  const bestMRR = getBestMetric(
    evaluation,
    "mrr",
  )

  const bestNDCG10 = getBestMetric(
    evaluation,
    "ndcg@10",
  )

  const bestHitRate10 = getBestMetric(
    evaluation,
    "hit_rate@10",
  )

  // =======================================================
  // QUERIES
  // =======================================================

  const queries =
    evaluation.dense.count

  // =======================================================
  // CARD
  // =======================================================

  return (
    <Card className="h-[500px] w-full overflow-hidden">

      {/* =================================================
          HEADER
      ================================================= */}

      <CardHeader className="pb-2">
        <CardTitle>
          Retrieval Quality
        </CardTitle>

        <CardDescription>
          Recall@K comparison — Dense vs Hybrid
          vs Reranked
        </CardDescription>
      </CardHeader>

      {/* =================================================
          CONTENT
      ================================================= */}

      <CardContent className="pt-0">

        {/* =================================================
            CHART
        ================================================= */}

        <ChartContainer
          config={chartConfig}
          className="h-[300px] w-full"
        >
          <LineChart
            accessibilityLayer
            data={chartData}
            margin={{
              top: 10,
              right: 20,
              left: 0,
              bottom: 10,
            }}
          >
            <CartesianGrid
              vertical={false}
              strokeDasharray="3 3"
            />

            <XAxis
              dataKey="k"
              tickLine={false}
              axisLine={false}
              tickMargin={10}
              padding={{
                left: 10,
                right: 10,
              }}
            />

            <YAxis
              domain={[0, 100]}
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              width={45}
              tickFormatter={(value) =>
                `${value}%`
              }
            />

            {/* =================================================
                TOOLTIP
            ================================================= */}

            <Tooltip
              cursor={{
                strokeDasharray: "4 4",
              }}
              content={(props) => (
                <RetrievalTooltip
                  active={props.active}
                  payload={props.payload}
                  label={props.label}
                />
              )}
            />

            {/* =================================================
                LEGEND
            ================================================= */}

            <ChartLegend
              verticalAlign="top"
              content={
                <ChartLegendContent />
              }
              className="mb-2"
            />

            {/* =================================================
                DENSE
            ================================================= */}

            <Line
              dataKey="dense"
              type="monotone"
              stroke="var(--color-dense)"
              strokeWidth={3}
              dot={{
                r: 4,
                fill: "var(--color-dense)",
                strokeWidth: 0,
              }}
              activeDot={{
                r: 6,
                fill: "var(--color-dense)",
                strokeWidth: 0,
              }}
            />

            {/* =================================================
                HYBRID
            ================================================= */}

            <Line
              dataKey="hybrid"
              type="monotone"
              stroke="var(--color-hybrid)"
              strokeWidth={3}
              dot={{
                r: 4,
                fill: "var(--color-hybrid)",
                strokeWidth: 0,
              }}
              activeDot={{
                r: 6,
                fill: "var(--color-hybrid)",
                strokeWidth: 0,
              }}
            />

            {/* =================================================
                RERANKED
            ================================================= */}

            <Line
              dataKey="reranked"
              type="monotone"
              stroke="var(--color-reranked)"
              strokeWidth={3}
              dot={{
                r: 4,
                fill: "var(--color-reranked)",
                strokeWidth: 0,
              }}
              activeDot={{
                r: 6,
                fill: "var(--color-reranked)",
                strokeWidth: 0,
              }}
            />
          </LineChart>
        </ChartContainer>

        {/* =================================================
            SUMMARY
        ================================================= */}

        <div className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-4">

          {/* =================================================
              BEST MRR
          ================================================= */}

          <div className="rounded-lg border p-3">
            <p className="text-xs text-muted-foreground">
              Best MRR
            </p>

            <p className="mt-1 text-xl font-semibold">
              {bestMRR.value.toFixed(4)}
            </p>

            <p
              className="mt-1 text-xs font-medium"
              style={{
                color:
                  chartConfig[
                    bestMRR.key
                  ].color,
              }}
            >
              {bestMRR.name}
            </p>
          </div>

          {/* =================================================
              BEST NDCG
          ================================================= */}

          <div className="rounded-lg border p-3">
            <p className="text-xs text-muted-foreground">
              Best nDCG@10
            </p>

            <p className="mt-1 text-xl font-semibold">
              {bestNDCG10.value.toFixed(4)}
            </p>

            <p
              className="mt-1 text-xs font-medium"
              style={{
                color:
                  chartConfig[
                    bestNDCG10.key
                  ].color,
              }}
            >
              {bestNDCG10.name}
            </p>
          </div>

          {/* =================================================
              BEST HIT RATE
          ================================================= */}

          <div className="rounded-lg border p-3">
            <p className="text-xs text-muted-foreground">
              Best Hit Rate@10
            </p>

            <p className="mt-1 text-xl font-semibold">
              {(
                bestHitRate10.value *
                100
              ).toFixed(1)}
              %
            </p>

            <p
              className="mt-1 text-xs font-medium"
              style={{
                color:
                  chartConfig[
                    bestHitRate10.key
                  ].color,
              }}
            >
              {bestHitRate10.name}
            </p>
          </div>

          {/* =================================================
              QUERIES
          ================================================= */}

          <div className="rounded-lg border p-3">
            <p className="text-xs text-muted-foreground">
              Queries
            </p>

            <p className="mt-1 text-xl font-semibold">
              {queries}
            </p>

            <p className="mt-1 text-xs text-muted-foreground">
              Evaluation dataset
            </p>
          </div>

        </div>
      </CardContent>
    </Card>
  )
}
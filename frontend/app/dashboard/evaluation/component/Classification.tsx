"use client"

import { useEffect, useState } from "react"
import {
  Bar,
  BarChart,
  CartesianGrid,
  XAxis,
} from "recharts"

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"

type Evaluation = {
  key: string
  node: string
  accuracy: number
  precision: number
  recall: number
  f1: number
}

export function ChartBarMultiple() {
  const [evaluations, setEvaluations] = useState<Evaluation[]>([])

  useEffect(() => {
    const fetchEvaluations = async () => {
      try {
        const res = await fetch(
          "http://localhost:8000/api/v1/evaluation/classification"
        )

        if (!res.ok) {
          throw new Error(`HTTP error: ${res.status}`)
        }

        const data = await res.json()

        const evaluations: Evaluation[] = [
          {
            key: "router",
            node: data.router.node,
            accuracy: data.router.accuracy,
            precision: data.router.precision,
            recall: data.router.recall,
            f1: data.router.f1,
          },
          {
            key: "memory",
            node: "Memory",
            accuracy: data.retrieval_planner.memory.accuracy,
            precision: data.retrieval_planner.memory.precision,
            recall: data.retrieval_planner.memory.recall,
            f1: data.retrieval_planner.memory.f1,
          },
          {
            key: "vector",
            node: "Vector",
            accuracy: data.retrieval_planner.vector.accuracy,
            precision: data.retrieval_planner.vector.precision,
            recall: data.retrieval_planner.vector.recall,
            f1: data.retrieval_planner.vector.f1,
          },
          {
            key: "repo",
            node: "Repo",
            accuracy: data.retrieval_planner.repo.accuracy,
            precision: data.retrieval_planner.repo.precision,
            recall: data.retrieval_planner.repo.recall,
            f1: data.retrieval_planner.repo.f1,
          },
        ]

        setEvaluations(evaluations)
      } catch (error) {
        console.error("Failed to fetch evaluations:", error)
      }
    }

    fetchEvaluations()
  }, [])

  const chartData = [
    {
      metric: "Accuracy",
      ...Object.fromEntries(
        evaluations.map((item) => [
          item.key,
          item.accuracy * 100,
        ])
      ),
    },
    {
      metric: "Precision",
      ...Object.fromEntries(
        evaluations.map((item) => [
          item.key,
          item.precision * 100,
        ])
      ),
    },
    {
      metric: "Recall",
      ...Object.fromEntries(
        evaluations.map((item) => [
          item.key,
          item.recall * 100,
        ])
      ),
    },
    {
      metric: "F1",
      ...Object.fromEntries(
        evaluations.map((item) => [
          item.key,
          item.f1 * 100,
        ])
      ),
    },
  ]

  const chartConfig: ChartConfig = Object.fromEntries(
    evaluations.map((item, index) => [
      item.key,
      {
        label: item.node,
        color: `var(--chart-${index + 1})`,
      },
    ])
  )

  return (
    <Card className="w-[30%] h-[30%]">
      <CardHeader>
        <CardTitle>Classification Evaluation</CardTitle>
      </CardHeader>

      <CardContent>
        {evaluations.length > 0 && (
          <ChartContainer config={chartConfig}>
            <BarChart
              accessibilityLayer
              data={chartData}
            >
              <CartesianGrid vertical={false} />

              <XAxis
                dataKey="metric"
                tickLine={false}
                tickMargin={10}
                axisLine={false}
              />

              <ChartTooltip
                cursor={false}
                content={
                  <ChartTooltipContent indicator="dashed" />
                }
              />

              {evaluations.map((item) => (
                <Bar
                  key={item.key}
                  dataKey={item.key}
                  fill={`var(--color-${item.key})`}
                  radius={4}
                />
              ))}
            </BarChart>
          </ChartContainer>
        )}
      </CardContent>
    </Card>
  )
}
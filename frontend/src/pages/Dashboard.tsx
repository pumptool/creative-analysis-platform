import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { experimentApi, Experiment } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { formatDate, formatPercentage, getStatusColor } from '@/lib/utils'
import { Loader2, Plus, TrendingUp, TrendingDown, AlertCircle } from 'lucide-react'

export function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['experiments'],
    queryFn: () => experimentApi.list(),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
          <p className="text-lg font-medium">Failed to load experiments</p>
          <p className="text-sm text-muted-foreground">Please try again later</p>
        </div>
      </div>
    )
  }

  const experiments: Experiment[] = data?.experiments || []

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Experiments</h1>
          <p className="text-muted-foreground">
            Manage and analyze your creative pre-testing experiments
          </p>
        </div>
        <Link to="/experiments/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New Experiment
          </Button>
        </Link>
      </div>

      {experiments.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <p className="text-lg font-medium mb-2">No experiments yet</p>
            <p className="text-sm text-muted-foreground mb-4">
              Get started by creating your first experiment
            </p>
            <Link to="/experiments/new">
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Create Experiment
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {experiments.map((experiment) => (
            <ExperimentCard key={experiment.id} experiment={experiment} />
          ))}
        </div>
      )}
    </div>
  )
}

function ExperimentCard({ experiment }: { experiment: Experiment }) {
  const summary = experiment.summary

  return (
    <Link to={`/experiments/${experiment.id}`}>
      <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
        <CardHeader>
          <div className="flex items-start justify-between">
            <CardTitle className="text-lg">{experiment.title}</CardTitle>
            <Badge className={getStatusColor(experiment.status)}>
              {experiment.status}
            </Badge>
          </div>
          <CardDescription className="line-clamp-2">
            {experiment.description || 'No description'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {experiment.status === 'completed' && summary ? (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-4">
                <MetricDisplay
                  label="Favorability"
                  value={summary.overall_favorability}
                />
                <MetricDisplay
                  label="Purchase Intent"
                  value={summary.overall_intent}
                />
              </div>
              <div className="pt-3 border-t">
                <p className="text-sm text-muted-foreground">
                  {summary.recommendation_count} recommendations
                </p>
                {summary.top_segment && (
                  <p className="text-xs text-muted-foreground mt-1">
                    Top: {summary.top_segment}
                  </p>
                )}
              </div>
            </div>
          ) : experiment.status === 'processing' ? (
            <div className="flex items-center text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
              Analysis in progress...
            </div>
          ) : experiment.status === 'failed' ? (
            <div className="text-sm text-destructive">
              <AlertCircle className="h-4 w-4 inline mr-1" />
              Analysis failed
            </div>
          ) : (
            <div className="text-sm text-muted-foreground">
              Ready to analyze
            </div>
          )}
          <div className="mt-4 text-xs text-muted-foreground">
            Created {formatDate(experiment.created_at)}
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}

function MetricDisplay({ label, value }: { label: string; value?: number }) {
  if (value === undefined) return null

  const isPositive = value > 0
  const Icon = isPositive ? TrendingUp : TrendingDown

  return (
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <div className="flex items-center mt-1">
        <Icon
          className={`h-4 w-4 mr-1 ${
            isPositive ? 'text-green-600' : 'text-red-600'
          }`}
        />
        <span
          className={`text-lg font-semibold ${
            isPositive ? 'text-green-600' : 'text-red-600'
          }`}
        >
          {formatPercentage(value)}
        </span>
      </div>
    </div>
  )
}

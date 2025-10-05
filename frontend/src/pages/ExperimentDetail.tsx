import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { experimentApi, Recommendation } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import {
  ArrowLeft,
  Play,
  Download,
  Loader2,
  TrendingUp,
  TrendingDown,
  AlertCircle,
} from 'lucide-react'
import { formatPercentage, getStatusColor, getPriorityColor, downloadBlob } from '@/lib/utils'

export function ExperimentDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [selectedSegment, setSelectedSegment] = useState<string | undefined>()
  const [selectedGoal, setSelectedGoal] = useState<string | undefined>()

  const { data: experiment, isLoading } = useQuery({
    queryKey: ['experiment', id],
    queryFn: () => experimentApi.get(id!),
    enabled: !!id,
  })

  const { data: recommendationsData } = useQuery({
    queryKey: ['recommendations', id, selectedSegment, selectedGoal],
    queryFn: () =>
      experimentApi.getRecommendations(id!, {
        segment: selectedSegment,
        brand_goal: selectedGoal,
      }),
    enabled: !!id && experiment?.status === 'completed',
  })

  const analyzeMutation = useMutation({
    mutationFn: () => experimentApi.triggerAnalysis(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['experiment', id] })
    },
  })

  const exportPdfMutation = useMutation({
    mutationFn: () => experimentApi.exportPdf(id!),
    onSuccess: (blob) => {
      downloadBlob(blob, `${experiment?.title}_report.pdf`)
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!experiment) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
          <p className="text-lg font-medium">Experiment not found</p>
        </div>
      </div>
    )
  }

  const recommendations: Recommendation[] = recommendationsData?.recommendations || []
  const summary = experiment.summary

  // Get unique segments and goals
  const segments = [...new Set(recommendations.map((r) => r.segment))]
  const goals = [...new Set(recommendations.map((r) => r.brand_goal))]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-4">
          <Button variant="ghost" onClick={() => navigate('/')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{experiment.title}</h1>
            <p className="text-muted-foreground mt-1">{experiment.description}</p>
            <div className="mt-2">
              <Badge className={getStatusColor(experiment.status)}>
                {experiment.status}
              </Badge>
            </div>
          </div>
        </div>

        <div className="flex space-x-2">
          {experiment.status === 'pending' && (
            <Button
              onClick={() => analyzeMutation.mutate()}
              disabled={analyzeMutation.isPending}
            >
              {analyzeMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Starting...
                </>
              ) : (
                <>
                  <Play className="mr-2 h-4 w-4" />
                  Start Analysis
                </>
              )}
            </Button>
          )}

          {experiment.status === 'completed' && (
            <Button
              variant="outline"
              onClick={() => exportPdfMutation.mutate()}
              disabled={exportPdfMutation.isPending}
            >
              {exportPdfMutation.isPending ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Download className="mr-2 h-4 w-4" />
              )}
              Export PDF
            </Button>
          )}
        </div>
      </div>

      {/* Summary Metrics */}
      {experiment.status === 'completed' && summary && (
        <div className="grid gap-4 md:grid-cols-3">
          <MetricCard
            title="Brand Favorability"
            value={summary.overall_favorability}
          />
          <MetricCard
            title="Purchase Intent"
            value={summary.overall_intent}
          />
          <MetricCard
            title="Brand Associations"
            value={summary.overall_associations}
          />
        </div>
      )}

      {/* Processing Status */}
      {experiment.status === 'processing' && (
        <Card>
          <CardContent className="py-8">
            <div className="flex items-center justify-center">
              <Loader2 className="h-8 w-8 animate-spin text-primary mr-3" />
              <div>
                <p className="font-medium">Analysis in progress...</p>
                <p className="text-sm text-muted-foreground">
                  This may take a few minutes
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recommendations */}
      {experiment.status === 'completed' && (
        <Card>
          <CardHeader>
            <CardTitle>Creative Recommendations</CardTitle>
            <CardDescription>
              Actionable insights to improve your creative performance
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Filters */}
            <div className="flex space-x-4 mb-6">
              <div className="flex-1">
                <label className="block text-sm font-medium mb-2">Segment</label>
                <select
                  className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
                  value={selectedSegment || ''}
                  onChange={(e) => setSelectedSegment(e.target.value || undefined)}
                >
                  <option value="">All Segments</option>
                  {segments.map((seg) => (
                    <option key={seg} value={seg}>
                      {seg}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex-1">
                <label className="block text-sm font-medium mb-2">Brand Goal</label>
                <select
                  className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
                  value={selectedGoal || ''}
                  onChange={(e) => setSelectedGoal(e.target.value || undefined)}
                >
                  <option value="">All Goals</option>
                  {goals.map((goal) => (
                    <option key={goal} value={goal}>
                      {goal.replace(/_/g, ' ')}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Recommendation List */}
            <div className="space-y-4">
              {recommendations.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">
                  No recommendations found
                </p>
              ) : (
                recommendations.map((rec) => (
                  <RecommendationCard key={rec.id} recommendation={rec} />
                ))
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function MetricCard({ title, value }: { title: string; value?: number }) {
  if (value === undefined) return null

  const isPositive = value > 0
  const Icon = isPositive ? TrendingUp : TrendingDown

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription>{title}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-center">
          <Icon
            className={`h-6 w-6 mr-2 ${
              isPositive ? 'text-green-600' : 'text-red-600'
            }`}
          />
          <span
            className={`text-3xl font-bold ${
              isPositive ? 'text-green-600' : 'text-red-600'
            }`}
          >
            {formatPercentage(value)}
          </span>
        </div>
      </CardContent>
    </Card>
  )
}

function RecommendationCard({ recommendation }: { recommendation: Recommendation }) {
  return (
    <div className="border border-input rounded-lg p-4 hover:bg-accent/50 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-1">
            <Badge className={getPriorityColor(recommendation.priority)}>
              {recommendation.priority}
            </Badge>
            <Badge variant="outline">{recommendation.type}</Badge>
          </div>
          <h3 className="font-semibold text-lg">{recommendation.creative_element}</h3>
          <p className="text-sm text-muted-foreground">
            {recommendation.segment} • {recommendation.brand_goal.replace(/_/g, ' ')}
          </p>
        </div>
        {recommendation.impact_score && (
          <div className="text-right">
            <p className="text-xs text-muted-foreground">Impact Score</p>
            <p className="text-lg font-bold">{recommendation.impact_score.toFixed(3)}</p>
          </div>
        )}
      </div>

      <p className="text-sm mb-4">{recommendation.justification}</p>

      {recommendation.quantitative_support && (
        <div className="bg-muted/50 rounded-md p-3 mb-3">
          <p className="text-xs font-medium mb-2">Quantitative Evidence</p>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-muted-foreground">Delta:</span>{' '}
              <span className="font-medium">
                {formatPercentage(recommendation.quantitative_support.delta)}
              </span>
            </div>
            <div>
              <span className="text-muted-foreground">Significant:</span>{' '}
              <span className="font-medium">
                {recommendation.quantitative_support.statistical_significance
                  ? 'Yes'
                  : 'No'}
              </span>
            </div>
          </div>
        </div>
      )}

      {recommendation.qualitative_support && recommendation.qualitative_support.length > 0 && (
        <div>
          <p className="text-xs font-medium mb-2">Audience Feedback</p>
          <div className="space-y-1">
            {recommendation.qualitative_support.slice(0, 2).map((support, idx) => (
              <p key={idx} className="text-xs text-muted-foreground italic">
                "{support.comment}"
              </p>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

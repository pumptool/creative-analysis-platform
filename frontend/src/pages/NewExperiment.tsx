import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { experimentApi } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { ArrowLeft, Upload, Loader2 } from 'lucide-react'

export function NewExperiment() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    videoFile: null as File | null,
    videoUrl: '',
    resultsCSV: null as File | null,
    commentsCSV: null as File | null,
  })

  const createMutation = useMutation({
    mutationFn: async (data: FormData) => {
      return experimentApi.create(data)
    },
    onSuccess: (data) => {
      navigate(`/experiments/${data.id}`)
    },
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const data = new FormData()
    data.append('title', formData.title)
    if (formData.description) {
      data.append('description', formData.description)
    }

    if (formData.videoFile) {
      data.append('video_file', formData.videoFile)
    } else if (formData.videoUrl) {
      data.append('video_url', formData.videoUrl)
    }

    if (formData.resultsCSV) {
      data.append('results_csv', formData.resultsCSV)
    }

    if (formData.commentsCSV) {
      data.append('comments_csv', formData.commentsCSV)
    }

    createMutation.mutate(data)
  }

  const isValid =
    formData.title &&
    (formData.videoFile || formData.videoUrl) &&
    formData.resultsCSV &&
    formData.commentsCSV

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center space-x-4">
        <Button variant="ghost" onClick={() => navigate('/')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">New Experiment</h1>
          <p className="text-muted-foreground">
            Upload your creative and pre-testing data
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle>Experiment Details</CardTitle>
            <CardDescription>
              Provide information about your creative pre-testing experiment
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Title */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Title <span className="text-destructive">*</span>
              </label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
                value={formData.title}
                onChange={(e) =>
                  setFormData({ ...formData, title: e.target.value })
                }
                placeholder="Q4 Brand Campaign Test"
                required
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Description
              </label>
              <textarea
                className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
                rows={3}
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                placeholder="Brief description of the experiment..."
              />
            </div>

            {/* Video Upload */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Video Creative <span className="text-destructive">*</span>
              </label>
              <div className="space-y-3">
                <div className="border-2 border-dashed border-input rounded-lg p-6 text-center">
                  <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                  <input
                    type="file"
                    accept="video/*"
                    className="hidden"
                    id="video-upload"
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        videoFile: e.target.files?.[0] || null,
                        videoUrl: '',
                      })
                    }
                  />
                  <label
                    htmlFor="video-upload"
                    className="cursor-pointer text-sm text-primary hover:underline"
                  >
                    Click to upload video file
                  </label>
                  {formData.videoFile && (
                    <p className="text-sm text-muted-foreground mt-2">
                      {formData.videoFile.name}
                    </p>
                  )}
                </div>

                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-background px-2 text-muted-foreground">
                      Or
                    </span>
                  </div>
                </div>

                <input
                  type="url"
                  className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
                  value={formData.videoUrl}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      videoUrl: e.target.value,
                      videoFile: null,
                    })
                  }
                  placeholder="https://example.com/video.mp4"
                  disabled={!!formData.videoFile}
                />
              </div>
            </div>

            {/* Results CSV */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Quantitative Results CSV <span className="text-destructive">*</span>
              </label>
              <input
                type="file"
                accept=".csv"
                className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    resultsCSV: e.target.files?.[0] || null,
                  })
                }
                required
              />
              {formData.resultsCSV && (
                <p className="text-sm text-muted-foreground mt-1">
                  {formData.resultsCSV.name}
                </p>
              )}
            </div>

            {/* Comments CSV */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Qualitative Comments CSV <span className="text-destructive">*</span>
              </label>
              <input
                type="file"
                accept=".csv"
                className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    commentsCSV: e.target.files?.[0] || null,
                  })
                }
                required
              />
              {formData.commentsCSV && (
                <p className="text-sm text-muted-foreground mt-1">
                  {formData.commentsCSV.name}
                </p>
              )}
            </div>

            {/* Error Message */}
            {createMutation.isError && (
              <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-md text-sm">
                Failed to create experiment. Please try again.
              </div>
            )}

            {/* Submit Button */}
            <div className="flex justify-end space-x-3">
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate('/')}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={!isValid || createMutation.isPending}>
                {createMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  'Create Experiment'
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  )
}

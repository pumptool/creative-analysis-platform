import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'
import { Dashboard } from '@/pages/Dashboard'
import { ExperimentDetail } from '@/pages/ExperimentDetail'
import { NewExperiment } from '@/pages/NewExperiment'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/experiments/new" element={<NewExperiment />} />
          <Route path="/experiments/:id" element={<ExperimentDetail />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App

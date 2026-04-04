import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import HomePage from './pages/HomePage'
import FeaturesPage from './pages/FeaturesPage'
import AboutPage from './pages/AboutPage'
import ListingDetail from './pages/ListingDetail'
import CompanyResearch from './pages/CompanyResearch'
import ScrollToTop from './components/ScrollToTop'

function App() {
  return (
    <>
      <ScrollToTop />
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/features" element={<FeaturesPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/staj/:id" element={<ListingDetail />} />
          <Route path="/company-research/:name" element={<CompanyResearch />} />
        </Routes>
      </main>
      <Footer />
    </>
  )
}

export default App

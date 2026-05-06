import { Route, Routes } from 'react-router-dom'
import Footer from './components/Footer'
import Navbar from './components/Navbar'
import ScrollToTop from './components/ScrollToTop'
import AboutPage from './pages/AboutPage'
import AccountPage from './pages/AccountPage'
import AgentPage from './pages/AgentPage'
import CompanyResearch from './pages/CompanyResearch'
import FeaturesPage from './pages/FeaturesPage'
import HomePage from './pages/HomePage'
import ListingDetail from './pages/ListingDetail'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'

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
          <Route path="/giris" element={<LoginPage />} />
          <Route path="/kayit" element={<RegisterPage />} />
          <Route path="/hesabim" element={<AccountPage />} />
          <Route path="/staj/:id" element={<ListingDetail />} />
          <Route path="/company-research/:name" element={<CompanyResearch />} />
          <Route path="/ajan" element={<AgentPage />} />
        </Routes>
      </main>
      <Footer />
    </>
  )
}

export default App

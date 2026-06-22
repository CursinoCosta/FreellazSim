import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext.jsx'
import RotaPrivada from './components/RotaPrivada.jsx'
import Home from './pages/Home.jsx'
import Login from './pages/Login.jsx'
import Cadastro from './pages/Cadastro.jsx'
import ServicoDetalhes from './pages/ServicoDetalhes.jsx'
import DashboardCliente from './pages/DashboardCliente.jsx'
import DashboardFreelancer from './pages/DashboardFreelancer.jsx'
import './App.css'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter basename={import.meta.env.BASE_URL}>
        <div id="app">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/cadastro" element={<Cadastro />} />
            <Route path="/servicos/:id" element={<ServicoDetalhes />} />
            <Route
              path="/dashboard/cliente"
              element={
                <RotaPrivada>
                  <DashboardCliente />
                </RotaPrivada>
              }
            />
            <Route
              path="/dashboard/freelancer"
              element={
                <RotaPrivada>
                  <DashboardFreelancer />
                </RotaPrivada>
              }
            />
          </Routes>
        </div>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App

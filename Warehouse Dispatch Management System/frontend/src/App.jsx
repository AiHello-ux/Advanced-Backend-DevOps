import { Routes, Route, Link } from 'react-router-dom';
import RegisterPackagePage from './pages/RegisterPackagePage';
import PackageDetailPage from './pages/PackageDetailPage';

export default function App() {
  return (
    <>
      <nav style={{ display: 'flex', gap: '15px', padding: '10px' }}>
        <Link to="/">Register Package</Link>
      </nav>

      <Routes>
        <Route path="/" element={<RegisterPackagePage />} />
        <Route path="/packages/:id" element={<PackageDetailPage />} />
      </Routes>
    </>
  );
}
'use client'; 

import { useState, useEffect } from 'react';
import LeadList from '../components/LeadList';
import LeadDetails from '../components/LeadDetails';
import StatsBlock from '../components/StatsBlock';
import KanbanBoard from '../components/KanbanBoard';

const API_URL = 'http://192.168.1.66:5000';

export default function Home() {
  const [leads, setLeads] = useState([]); // Состояние для списка лидов
  const [selectedLead, setSelectedLead] = useState(null); // Состояние для выбранного лида
  const [isModalOpen, setIsModalOpen] = useState(false); // Состояние для модального окна
  const [isLoading, setIsLoading] = useState(true); // Состояние для индикатора загрузки
  const [error, setError] = useState(null); // Состояние для ошибок
  const [stats, setStats] = useState({ total: 0, accepted: 0, in_progress: 0, declined: 0, clients: 0, total_revenue: 0 });
  const [revenue, setRevenue] = useState(0);
  const [period, setPeriod] = useState('all');
  const [customDates, setCustomDates] = useState({ start: '', end: '' });

  useEffect(() => {
    setIsLoading(true); // Установка индикатора загрузки
    fetch(`${API_URL}/leads`) // Запрос на получение списка лидов
      .then(res => {
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      })
      .then(data => {
        setLeads(data); // Обновление состояния списка лидов
        setError(null); // Сброс ошибки
      })
      .catch(err => {
        console.error("Failed to fetch leads:", err);
        setError('Не удалось загрузить лиды. Проверьте, запущен ли бэкенд.'); // Установка ошибки
        setLeads([]); // Сброс списка лидов
      })
      .finally(() => {
        setIsLoading(false); // Сброс индикатора загрузки
      });
  }, []); // Хук useEffect с пустым массивом зависимостей

  useEffect(() => {
    // Загрузка статистики
    let url = `${API_URL}/stats`;
    let params = [];
    if (period === 'custom' && customDates.start && customDates.end) {
      params.push(`start_date=${customDates.start}`);
      params.push(`end_date=${customDates.end}`);
    } else if (period !== 'all') {
      params.push(`period=${period}`);
    }
    if (params.length) url += '?' + params.join('&');
    fetch(url)
      .then(res => res.json())
      .then(data => {
        setStats(data);
        setRevenue(data.revenue || 0); // Используем revenue из /stats вместо отдельного запроса
      })
      .catch(() => {
        setStats({ total: 0, accepted: 0, in_progress: 0, declined: 0, clients: 0, total_revenue: 0 });
        setRevenue(0);
      });

    // Убираем отдельный запрос к /revenue, так как используем данные из /stats
  }, [period, customDates]);

  const handleSelectLead = (lead) => {
    setSelectedLead(lead);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const handlePeriodChange = (e) => setPeriod(e.target.value);
  const handleCustomDateApply = () => {
    if (customDates.start && customDates.end) setPeriod('custom');
  };
  const handleResetDB = () => {
    if (!window.confirm('Вы уверены, что хотите обнулить базу лидов?')) return;
    fetch(`${API_URL}/reset`, { method: 'POST' })
      .then(res => res.json())
      .then(result => { if (result.success) window.location.reload(); else alert('Ошибка при сбросе базы'); })
      .catch(() => alert('Ошибка при сбросе базы'));
  };

  return (
    <main className="container mx-auto p-4 md:p-8">
      <StatsBlock
        stats={stats}
        revenue={revenue}
        period={period}
        customDates={customDates}
        setCustomDates={setCustomDates}
        onPeriodChange={handlePeriodChange}
        onCustomDateApply={handleCustomDateApply}
        onResetDB={handleResetDB}
      />
      {isLoading && <div className="text-center text-gray-500 py-4">Загрузка лидов...</div>}
      {error && <div className="text-center text-red-500 py-4 bg-red-100 border border-red-400 rounded">{error}</div>}
      {!isLoading && !error && (
        <KanbanBoard leads={leads} onSelect={handleSelectLead} />
      )}
      <LeadDetails 
        lead={selectedLead} 
        isOpen={isModalOpen} 
        onClose={handleCloseModal} 
      />
    </main>
  );
}

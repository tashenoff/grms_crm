'use client'; 

import { useState, useEffect } from 'react';
import LeadList from '../components/LeadList';
import LeadDetails from '../components/LeadDetails';
import StatsBlock from '../components/StatsBlock';
import KanbanBoard from '../components/KanbanBoard';
import AddLeadModal from '../components/AddLeadModal';
import EditLeadModal from '../components/EditLeadModal';
import { API_URL } from '../config';

export default function Home() {
  const [leads, setLeads] = useState([]); // Состояние для списка лидов
  const [selectedLead, setSelectedLead] = useState(null); // Состояние для выбранного лида
  const [isModalOpen, setIsModalOpen] = useState(false); // Состояние для модального окна деталей
  const [isAddModalOpen, setIsAddModalOpen] = useState(false); // Состояние для модального окна добавления
  const [isEditModalOpen, setIsEditModalOpen] = useState(false); // Состояние для модального окна редактирования
  const [editingLead, setEditingLead] = useState(null); // Состояние для редактируемой заявки
  const [isLoading, setIsLoading] = useState(true); // Состояние для индикатора загрузки
  const [error, setError] = useState(null); // Состояние для ошибок
  const [stats, setStats] = useState({ total: 0, accepted: 0, in_progress: 0, declined: 0, clients: 0, total_revenue: 0 });
  const [revenue, setRevenue] = useState(0);
  const [period, setPeriod] = useState('all');
  const [customDates, setCustomDates] = useState({ start: '', end: '' });

  // Функция для загрузки списка заявок
  const fetchLeads = () => {
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
  };

  useEffect(() => {
    fetchLeads();
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

  const handleOpenAddModal = () => {
    setIsAddModalOpen(true);
  };

  const handleCloseAddModal = () => {
    setIsAddModalOpen(false);
  };

  const handleOpenEditModal = (lead) => {
    setEditingLead(lead);
    setIsEditModalOpen(true);
  };

  const handleCloseEditModal = () => {
    setIsEditModalOpen(false);
    setEditingLead(null);
  };

  const handleLeadAdded = (newLead) => {
    // Обновляем список заявок после добавления новой
    fetchLeads();
  };

  const handleLeadUpdated = (updatedLead) => {
    // Обновляем список заявок после обновления
    fetchLeads();
  };

  const handleDeleteLead = (leadId) => {
    if (!window.confirm('Вы уверены, что хотите удалить эту заявку?')) {
      return;
    }

    fetch(`${API_URL}/delete_lead/${leadId}`, {
      method: 'POST',
    })
      .then(res => {
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      })
      .then(data => {
        if (data.success) {
          // Обновляем список заявок после удаления
          fetchLeads();
        } else {
          throw new Error(data.error || 'Не удалось удалить заявку');
        }
      })
      .catch(err => {
        console.error('Ошибка при удалении заявки:', err);
        alert(err.message);
      });
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
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">CRM-система</h1>
        <button 
          onClick={handleOpenAddModal}
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition flex items-center"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Добавить заявку
        </button>
      </div>
      
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
        <KanbanBoard 
          leads={leads} 
          onSelect={handleSelectLead}
          onEdit={handleOpenEditModal}
          onDelete={handleDeleteLead}
        />
      )}
      
      {/* Модальные окна */}
      <LeadDetails 
        lead={selectedLead} 
        isOpen={isModalOpen} 
        onClose={handleCloseModal} 
      />
      
      <AddLeadModal
        isOpen={isAddModalOpen}
        onClose={handleCloseAddModal}
        onLeadAdded={handleLeadAdded}
      />
      
      <EditLeadModal
        isOpen={isEditModalOpen}
        onClose={handleCloseEditModal}
        lead={editingLead}
        onLeadUpdated={handleLeadUpdated}
      />
    </main>
  );
}

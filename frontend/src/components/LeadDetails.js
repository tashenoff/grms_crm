'use client';
import React, { useState, useEffect } from 'react';
import Modal from './Modal';

const API_URL = 'http://192.168.1.66:5000';

export default function LeadDetails({ lead, isOpen, onClose }) {
  const [detailedLead, setDetailedLead] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Загружаем детальную информацию о заявке только если модальное окно открыто и есть ID заявки
    if (isOpen && lead && lead.id) {
      setIsLoading(true);
      setError(null);
      
      fetch(`${API_URL}/lead_details/${lead.id}`)
        .then(res => {
          if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
          }
          return res.json();
        })
        .then(data => {
          setDetailedLead(data);
          setError(null);
        })
        .catch(err => {
          console.error("Failed to fetch lead details:", err);
          setError('Не удалось загрузить детали заявки');
          // Используем базовые данные из списка заявок, если не удалось получить детали
          setDetailedLead(lead);
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [isOpen, lead]);

  // Если нет данных о заявке, возвращаем null
  if (!lead) return null;

  // Используем детальные данные, если они загружены, иначе используем базовые данные
  const displayLead = detailedLead || lead;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Детали заявки #${displayLead.id}`}
      size="lg"
    >
      {isLoading ? (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
          <p className="mt-2 text-gray-600">Загрузка деталей...</p>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          <p>{error}</p>
          <p className="text-sm mt-1">Отображаются базовые данные заявки</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg p-4 shadow-sm border-l-4 border-blue-500">
          <div className="flex justify-between items-center mb-4">
            <div className="font-semibold text-blue-600 text-lg">{displayLead.client_name || 'Клиент'}</div>
            <div className="text-sm text-gray-500">{new Date(displayLead.created_at).toLocaleString('ru-RU')}</div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div className="bg-gray-50 p-3 rounded">
              <div className="text-xs text-gray-500 mb-1">👤 Клиент</div>
              <div className="font-medium text-gray-900">{displayLead.client_name || 'Не указан'}</div>
            </div>
            
            {displayLead.company && (
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500 mb-1">🏢 Компания</div>
                <div className="font-medium text-gray-900">{displayLead.company}</div>
              </div>
            )}
            
            {displayLead.phone && (
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500 mb-1">📞 Телефон</div>
                <div className="font-medium text-gray-900">{displayLead.phone}</div>
              </div>
            )}
            
            {displayLead.email && (
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500 mb-1">✉️ Email</div>
                <div className="font-medium text-gray-900">{displayLead.email}</div>
              </div>
            )}
            
            {displayLead.city && (
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500 mb-1">🏙️ Город</div>
                <div className="font-medium text-gray-900">{displayLead.city}</div>
              </div>
            )}
            
            {displayLead.address && (
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500 mb-1">📍 Адрес</div>
                <div className="font-medium text-gray-900">{displayLead.address}</div>
              </div>
            )}
            
            {displayLead.source && (
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500 mb-1">📢 Источник</div>
                <div className="font-medium text-gray-900">{displayLead.source}</div>
              </div>
            )}
            
            {displayLead.total_amount && (
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500 mb-1">💰 Сумма</div>
                <div className="font-medium text-gray-900">{displayLead.total_amount}</div>
              </div>
            )}
            
            {displayLead.order_date && (
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-xs text-gray-500 mb-1">📅 Дата</div>
                <div className="font-medium text-gray-900">{displayLead.order_date}</div>
              </div>
            )}
          </div>
          
          {displayLead.order_details && (
            <div className="bg-gray-50 p-3 rounded mb-4">
              <div className="text-xs text-gray-500 mb-1">📦 Заказ</div>
              <div className="whitespace-pre-wrap text-sm bg-white p-3 rounded text-gray-900">
                {displayLead.order_details}
              </div>
            </div>
          )}
          
          <div className="flex justify-between items-center pt-3 border-t border-gray-200">
            <div>
              <span className="text-sm mr-2">Статус:</span>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusClass(displayLead.status)}`}>
                {getStatusText(displayLead.status)}
              </span>
            </div>
            {displayLead.executor_username && (
              <div className="text-sm text-gray-600">
                Исполнитель: {displayLead.executor_first_name || ''} (@{displayLead.executor_username})
              </div>
            )}
          </div>
          
          {displayLead.related_count > 1 && (
            <div className="mt-4 pt-3 border-t border-gray-200">
              <div className="text-sm text-gray-600">
                <span className="font-medium">Связанные заявки:</span> {displayLead.related_count - 1} шт.
              </div>
            </div>
          )}
        </div>
      )}
    </Modal>
  );
}

// Вспомогательные функции для отображения статуса
function getStatusClass(status) {
  switch (status) {
    case 'accepted':
      return 'bg-green-100 text-green-800';
    case 'declined':
      return 'bg-red-100 text-red-800';
    case 'in_progress':
      return 'bg-yellow-100 text-yellow-800';
    case 'delivery':
      return 'bg-cyan-100 text-cyan-800';
    default:
      return 'bg-blue-100 text-blue-800';
  }
}

function getStatusText(status) {
  switch (status) {
    case 'accepted':
      return 'Принято';
    case 'declined':
      return 'Отклонено';
    case 'in_progress':
      return 'В работе';
    case 'delivery':
      return 'Доставка';
    default:
      return 'Новая';
  }
}

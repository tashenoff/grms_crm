'use client';
import React from 'react';

export default function LeadCard({ lead, onSelect, onEdit, onDelete }) {
  // Функция для определения класса статуса
  const getStatusClass = (status) => {
    switch (status) {
      case 'new': 
      case 'processing':
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
      case 'accepted':
        return 'bg-green-100 text-green-800';
      case 'delivery': 
        return 'bg-blue-100 text-blue-800';
      case 'cancelled':
      case 'declined':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800'; 
    }
  };

  // Функция для получения текста статуса
  const getStatusText = (status) => {
    switch (status) {
      case 'new':
        return 'Новый';
      case 'in_progress':
        return 'В работе';
      case 'accepted':
        return 'Принято';
      case 'delivery': 
        return 'Доставка';
      case 'declined':
        return 'Отклонено';
      default:
        return status ? status.charAt(0).toUpperCase() + status.slice(1) : 'Неизвестен'; 
    }
  };

  // Обработчик клика по кнопке редактирования
  const handleEditClick = (e) => {
    e.stopPropagation(); // Остановка всплытия, чтобы не сработал обработчик клика по карточке
    onEdit && onEdit(lead);
  };

  // Обработчик клика по кнопке удаления
  const handleDeleteClick = (e) => {
    e.stopPropagation(); // Остановка всплытия, чтобы не сработал обработчик клика по карточке
    onDelete && onDelete(lead.id);
  };

  return (
    <div
      onClick={() => onSelect(lead)}
      className="cursor-pointer bg-white rounded-lg p-4 shadow-sm border-l-4 border-blue-500 relative group"
    >
      {/* Кнопки действий */}
      <div className="absolute top-2 right-2 flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
        {onEdit && (
          <button
            onClick={handleEditClick}
            className="text-blue-600 hover:text-blue-800 p-1 rounded-full hover:bg-blue-100"
            title="Редактировать заявку"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
            </svg>
          </button>
        )}
        
        {onDelete && (
          <button
            onClick={handleDeleteClick}
            className="text-red-600 hover:text-red-800 p-1 rounded-full hover:bg-red-100"
            title="Удалить заявку"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        )}
      </div>

      <div className="flex justify-between items-center mb-3">
        <div className="font-semibold text-blue-600">{lead.client_name || 'Клиент'}</div>
        <div className="text-xs text-gray-500">
          {lead.created_at}
          {lead.related_count > 1 ? 
            <span className="ml-2 bg-blue-100 text-blue-800 text-xs font-medium px-2 py-0.5 rounded-full">
              Заказов: {lead.related_count}
            </span> : ''}
        </div>
      </div>
      
      <div className="grid grid-cols-1 gap-2 mb-3">
        {lead.phone && <div className="text-sm text-gray-800"><span className="font-medium">📞</span> {lead.phone}</div>}
        {lead.city && <div className="text-sm text-gray-800"><span className="font-medium">🏙️</span> {lead.city}</div>}
        {lead.address && <div className="text-sm text-gray-800"><span className="font-medium">📍</span> {lead.address}</div>}
        {lead.total_amount && <div className="text-sm text-gray-800"><span className="font-medium">💰</span> {lead.total_amount}</div>}
        <div className="text-sm text-gray-800"><span className="font-medium">Источник:</span> {lead.source || '—'}</div>
        <div className="text-sm text-gray-800"><span className="font-medium">Исполнитель:</span> {lead.executor_username || 'Не назначен'}</div>
      </div>
      
      {lead.order_details && (
        <div className="text-sm mb-3">
          <div className="order-details bg-gray-50 p-2 rounded text-xs text-gray-800">
            {lead.order_details.length > 100 ? lead.order_details.substring(0, 100) + '...' : lead.order_details}
          </div>
        </div>
      )}
      
      <div className="flex justify-between items-center mt-2">
        <div>
          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusClass(lead.status)}`}>
            {getStatusText(lead.status)}
          </span>
        </div>
      </div>
    </div>
  );
}
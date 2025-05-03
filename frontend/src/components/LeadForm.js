'use client';
import React, { useState } from 'react';
import { API_URL } from '../config';

/**
 * Компонент формы для создания или редактирования заявки
 * @param {Object} props - Свойства компонента
 * @param {Object} props.lead - Заявка для редактирования (если null, то создается новая)
 * @param {Function} props.onSubmitSuccess - Функция, вызываемая после успешной отправки формы
 * @param {Function} props.onCancel - Функция, вызываемая при отмене
 * @returns {React.ReactElement}
 */
export default function LeadForm({ lead = null, onSubmitSuccess, onCancel }) {
  const isEditing = !!lead;
  
  const [formData, setFormData] = useState({
    client_name: lead?.client_name || '',
    phone: lead?.phone || '',
    email: lead?.email || '',
    message: lead?.message || '',
    source: lead?.source || 'web',
    status: lead?.status || 'new',
    order_details: lead?.order_details || '',
    total_amount: lead?.total_amount || ''
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    
    try {
      const url = isEditing 
        ? `${API_URL}/update_lead/${lead.id}` 
        : `${API_URL}/create_lead`;
      
      const method = 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      
      if (!response.ok) {
        throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      if (result.error) {
        throw new Error(result.error);
      }
      
      onSubmitSuccess(result);
    } catch (err) {
      console.error('Ошибка при отправке формы:', err);
      setError(err.message || 'Произошла ошибка при сохранении заявки');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="client_name" className="block text-sm font-medium text-gray-700">
            Имя клиента
          </label>
          <input
            type="text"
            id="client_name"
            name="client_name"
            value={formData.client_name}
            onChange={handleChange}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            placeholder="Имя клиента"
          />
        </div>
        
        <div>
          <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
            Телефон
          </label>
          <input
            type="text"
            id="phone"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            placeholder="+7 (XXX) XXX-XX-XX"
          />
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700">
            Email
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            placeholder="Email"
          />
        </div>
        
        <div>
          <label htmlFor="source" className="block text-sm font-medium text-gray-700">
            Источник
          </label>
          <select
            id="source"
            name="source"
            value={formData.source}
            onChange={handleChange}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
          >
            <option value="web">Веб-сайт</option>
            <option value="call">Звонок</option>
            <option value="email">Email</option>
            <option value="social">Социальные сети</option>
            <option value="other">Другое</option>
          </select>
        </div>
      </div>
      
      <div>
        <label htmlFor="message" className="block text-sm font-medium text-gray-700">
          Сообщение
        </label>
        <textarea
          id="message"
          name="message"
          value={formData.message}
          onChange={handleChange}
          rows="3"
          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
          placeholder="Сообщение клиента"
        />
      </div>
      
      <div>
        <label htmlFor="order_details" className="block text-sm font-medium text-gray-700">
          Детали заказа
        </label>
        <textarea
          id="order_details"
          name="order_details"
          value={formData.order_details}
          onChange={handleChange}
          rows="2"
          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
          placeholder="Детали заказа (опционально)"
        />
      </div>
      
      <div>
        <label htmlFor="total_amount" className="block text-sm font-medium text-gray-700">
          Сумма заказа
        </label>
        <input
          type="text"
          id="total_amount"
          name="total_amount"
          value={formData.total_amount}
          onChange={handleChange}
          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
          placeholder="Сумма заказа (опционально)"
        />
      </div>
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative">
          {error}
        </div>
      )}
      
      <div className="flex justify-end space-x-2">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
          disabled={isSubmitting}
        >
          Отмена
        </button>
        <button
          type="submit"
          className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Сохранение...' : isEditing ? 'Сохранить' : 'Создать'}
        </button>
      </div>
    </form>
  );
} 
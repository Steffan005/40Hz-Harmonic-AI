/**
 * OFFICE WINDOW - Individual Office View
 * Each office runs in its own independent Tauri window
 * Part of Phase 13: Multi-Window Office Support
 */

import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { OfficeChat } from '../components/OfficeChat';
import { TarotOffice } from '../components/offices/TarotOffice';
import { AstrologyOffice } from '../components/offices/AstrologyOffice';
import '../styles/office-window.css';

interface OfficeData {
  name: string;
  icon: string;
  description: string;
  specialists: Array<{ name: string }>;
}

export function OfficeWindow() {
  const { officeName } = useParams<{ officeName: string }>();
  const [officeData, setOfficeData] = useState<OfficeData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load office configuration from backend
    const loadOfficeConfig = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/office/${officeName}/config`);
        if (response.ok) {
          const data = await response.json();
          setOfficeData(data);
        } else {
          // Fallback to local office data
          setOfficeData({
            name: officeName || 'Unknown',
            icon: '🏛️',
            description: `${officeName} specialist office`,
            specialists: []
          });
        }
      } catch (error) {
        console.error('Failed to load office config:', error);
        // Fallback
        setOfficeData({
          name: officeName || 'Unknown',
          icon: '🏛️',
          description: `${officeName} specialist office`,
          specialists: []
        });
      } finally {
        setLoading(false);
      }
    };

    loadOfficeConfig();
  }, [officeName]);

  if (loading) {
    return (
      <div className="office-window loading">
        <div className="loading-spinner">
          <div className="quantum-pulse"></div>
          <p>Loading {officeName} office...</p>
        </div>
      </div>
    );
  }

  if (!officeData) {
    return (
      <div className="office-window error">
        <h2>Office Not Found</h2>
        <p>Could not load {officeName}</p>
      </div>
    );
  }

  // Render specialized office components for Tarot and Astrology
  const renderOfficeContent = () => {
    switch (officeName?.toLowerCase()) {
      case 'tarot':
        return <TarotOffice />;
      case 'astrologist':
      case 'astrology':
        return <AstrologyOffice />;
      default:
        // For all other offices, show chat interface
        return (
          <div className="office-content">
            <div className="office-info">
              <div className="office-icon">{officeData.icon}</div>
              <h1 className="office-name">{officeData.name}</h1>
              <p className="office-description">{officeData.description}</p>
            </div>

            <div className="office-chat-container">
              <OfficeChat
                officeName={officeData.name}
                officeId={officeName || ''}
                placeholder={`Ask ${officeData.name} specialist anything...`}
              />
            </div>

            {officeData.specialists.length > 0 && (
              <footer className="office-footer">
                <div className="specialists">
                  <span className="specialists-label">Specialists:</span>
                  {officeData.specialists.map((s, idx) => (
                    <span key={idx} className="specialist-tag">
                      {s.name}
                    </span>
                  ))}
                </div>
              </footer>
            )}
          </div>
        );
    }
  };

  return (
    <div className="office-window" data-office={officeName}>
      {renderOfficeContent()}
    </div>
  );
}

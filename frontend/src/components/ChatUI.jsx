import React, {useState, useEffect, useMemo} from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const TABS = [
  {id: 'plan', emoji: '🧠', label: 'Plan'},
  {id: 'usecases', emoji: '💡', label: 'Use Cases'},
  {id: 'targets', emoji: '🎯', label: 'Target Contact List'},
  {id: 'proposals', emoji: '📄', label: 'Proposals'},
]

export default function ChatUI({messages, setMessages, campaignId}){
  const [activeTab, setActiveTab] = useState('plan')
  
  // Extract structured campaign data from messages
  const campaignData = useMemo(() => {
    const data = { plan: {}, usecases: [], contacts: [], proposals: [], formattedText: '' }
    for (const msg of messages) {
      const content = msg.text || {}
      if (content.sections) {
        data.plan = content.sections.plan || {}
        data.usecases = content.sections.usecases?.use_cases || []
        data.contacts = content.sections.contacts?.contacts || []
      }
      if (content.data?.sections) {
        data.plan = content.data.sections.plan || data.plan
        data.usecases = content.data.sections.usecases?.use_cases || data.usecases
        data.contacts = content.data.sections.contacts?.contacts || data.contacts
        data.proposals = content.data.sections.content?.emails || []
      }
      if (content.formatted_text) {
        data.formattedText = content.formatted_text
      }
    }
    return data
  }, [messages])
  useEffect(() => {
    // attach handler to generate-content button
    const btn = document.getElementById('generate-content')
    if(!btn) return
    const handler = async () => {
      setMessages(prev => [...prev, {from: 'system', text: 'Requesting campaign content generation...'}])
      try{
        // Fire-and-forget POST; SSE will deliver generated content and formatted results.
        await fetch('http://localhost:8000/api/generate-content', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({campaign_id: campaignId})
        })
      }catch(err){
        setMessages(prev => [...prev, {from: 'system', text: 'Failed to generate content: '+String(err)}])
      }
    }

    btn.addEventListener('click', handler)
    return () => btn.removeEventListener('click', handler)
  }, [campaignId, setMessages])

  function renderPlanTab() {
    if (!campaignData.plan || !campaignData.plan.overview) {
      return <p className="text-gray-500 text-center py-8">Loading campaign plan...</p>
    }
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-bold text-blue-700">{campaignData.plan.overview}</h2>
        
        {campaignData.plan.timeline && (
          <div>
            <h3 className="text-lg font-semibold mb-2">📅 Timeline</h3>
            <div className="space-y-2">
              {campaignData.plan.timeline.map((week, i) => (
                <div key={i} className="p-3 bg-blue-50 rounded border-l-4 border-blue-500">
                  <span className="font-semibold">Week {week.week}</span>
                  <p className="text-gray-700">{week.activities?.join(', ')}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {campaignData.plan.channels && (
          <div>
            <h3 className="text-lg font-semibold mb-2">📢 Channels</h3>
            <div className="flex flex-wrap gap-2">
              {campaignData.plan.channels.map((ch, i) => (
                <span key={i} className="bg-blue-200 text-blue-800 px-3 py-1 rounded-full text-sm">
                  {ch}
                </span>
              ))}
            </div>
          </div>
        )}

        {campaignData.plan.goals && (
          <div>
            <h3 className="text-lg font-semibold mb-2">🎯 Goals</h3>
            <p className="text-gray-700">Meetings: <strong>{campaignData.plan.goals.meetings}</strong> | Responses: <strong>{campaignData.plan.goals.responses}</strong></p>
          </div>
        )}
      </div>
    )
  }

  function renderUseCasesTab() {
    if (campaignData.usecases.length === 0) {
      return <p className="text-gray-500 text-center py-8">Generating use cases...</p>
    }
    return (
      <div className="space-y-3">
        {campaignData.usecases.map((uc, i) => (
          <div key={i} className="p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded border border-green-200">
            <h4 className="font-semibold text-green-700">{uc.title}</h4>
            <p className="text-gray-700 text-sm mt-1">{uc.summary}</p>
            <div className="mt-2 flex justify-between items-center">
              <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                {uc.value_prop}
              </span>
              <button 
                onClick={() => alert(`Refine use case: ${uc.title}`)}
                className="text-xs bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600"
              >
                Generate Pitch
              </button>
            </div>
          </div>
        ))}
      </div>
    )
  }

  function renderTargetsTab() {
    if (campaignData.contacts.length === 0) {
      return <p className="text-gray-500 text-center py-8">Finding target contacts...</p>
    }
    return (
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="bg-blue-100">
              <th className="border border-gray-300 p-2 text-left">Name</th>
              <th className="border border-gray-300 p-2 text-left">Role</th>
              <th className="border border-gray-300 p-2 text-left">Company</th>
              <th className="border border-gray-300 p-2 text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {campaignData.contacts.map((c, i) => (
              <tr key={i} className="hover:bg-gray-50">
                <td className="border border-gray-300 p-2">{c.name}</td>
                <td className="border border-gray-300 p-2">{c.role}</td>
                <td className="border border-gray-300 p-2">{c.company}</td>
                <td className="border border-gray-300 p-2 flex gap-1">
                  <button 
                    onClick={() => alert(`Start contact: ${c.name}`)}
                    className="text-xs bg-green-500 text-white px-2 py-1 rounded hover:bg-green-600"
                  >
                    Start Contact
                  </button>
                  <button 
                    onClick={() => alert(`Generate message for ${c.name}`)}
                    className="text-xs bg-blue-500 text-white px-2 py-1 rounded hover:bg-blue-600"
                  >
                    Generate Message
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  function renderProposalsTab() {
    if (campaignData.proposals.length === 0) {
      return <p className="text-gray-500 text-center py-8">Generating proposals...</p>
    }
    return (
      <div className="space-y-4">
        {campaignData.proposals.map((prop, i) => (
          <div key={i} className="p-4 bg-yellow-50 rounded border border-yellow-200">
            <h4 className="font-semibold text-yellow-900">To: {prop.to}</h4>
            <p className="text-sm text-gray-600 mt-1"><strong>Subject:</strong> {prop.subject}</p>
            <div className="mt-2 p-2 bg-white rounded text-sm text-gray-700 whitespace-pre-wrap">
              {prop.body}
            </div>
            <button 
              onClick={() => alert(`Copy email to: ${prop.to}`)}
              className="mt-2 text-xs bg-yellow-600 text-white px-3 py-1 rounded hover:bg-yellow-700"
            >
              Copy Email
            </button>
          </div>
        ))}
      </div>
    )
  }

  function renderTabContent() {
    switch(activeTab) {
      case 'plan': return renderPlanTab()
      case 'usecases': return renderUseCasesTab()
      case 'targets': return renderTargetsTab()
      case 'proposals': return renderProposalsTab()
      default: return null
    }
  }

  function renderMessage(msg){
    const content = msg.text || {}
    if (content.formatted_text) {
      return <pre className="whitespace-pre-wrap text-sm bg-gray-100 p-2 rounded">{content.formatted_text}</pre>
    }
    switch(content.type){
      case 'status':
        return <p className="text-gray-600 text-sm animate-pulse">⏳ {content.message}</p>
      case 'result':
        if (content.data && content.data.formatted_text) {
          return <pre className="whitespace-pre-wrap text-xs bg-gray-100 p-2 rounded">{content.data.formatted_text}</pre>
        }
        return <p className="text-xs text-gray-600">✓ {content.data?.agent || 'Agent'} completed</p>
      case 'complete':
        return <p className="text-green-600 font-semibold text-sm">✅ {content.message}</p>
      default:
        return <pre className="whitespace-pre-wrap text-xs">{JSON.stringify(content, null, 2)}</pre>
    }
  }

  return (
    <div>
      {/* tabs */}
      <nav className="mb-4 border-b border-gray-300">
        <div className="flex gap-2">
          {TABS.map(tab => (
            <motion.button 
              key={tab.id} 
              onClick={()=>setActiveTab(tab.id)}
              className={`px-4 py-3 font-medium transition-all ${activeTab === tab.id ? 'border-b-2 border-blue-600 text-blue-600 bg-blue-50' : 'text-gray-600 hover:text-gray-800'}`}
              whileHover={{scale: 1.05}}
              whileTap={{scale: 0.95}}
            >
              <span className="mr-2">{tab.emoji}</span>
              {tab.label}
            </motion.button>
          ))}
        </div>
      </nav>

      {/* tab content - either messages log or structured data display */}
      <div className="mb-6">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{opacity: 0, y: 10}}
            animate={{opacity: 1, y: 0}}
            exit={{opacity: 0, y: -10}}
            transition={{duration: 0.2}}
            className="p-4 bg-white rounded border border-gray-200 min-h-96"
          >
            {renderTabContent()}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* messages log - optional, collapsible */}
      {messages.length > 0 && (
        <details className="mb-6 p-4 bg-gray-50 rounded border border-gray-200">
          <summary className="cursor-pointer font-semibold text-gray-700">Agent Messages ({messages.length})</summary>
          <div className="mt-4 space-y-2 max-h-64 overflow-y-auto">
            <AnimatePresence>
              {messages.map((msg, i) => (
                <motion.div 
                  key={i} 
                  initial={{opacity:0, x: -10}} 
                  animate={{opacity:1, x: 0}}
                  exit={{opacity: 0, x: 10}}
                  className="p-2 rounded bg-gray-100 text-xs"
                >
                  <div className="font-medium text-gray-600 mb-1">{msg.from}</div>
                  {renderMessage(msg)}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </details>
      )}

      {/* actions bar */}
      <div className="mt-6 flex justify-between gap-2 flex-wrap">
        <button 
          id="generate-content" 
          className="bg-blue-600 text-white px-6 py-2 rounded font-semibold hover:bg-blue-700 transition-colors"
        >
          Generate Campaign Content
        </button>
        <button 
          className="border border-gray-300 text-gray-700 px-6 py-2 rounded font-semibold hover:bg-gray-100 transition-colors" 
          onClick={()=>window.location.reload()}
        >
          Start New Campaign
        </button>
      </div>
    </div>
  )
}
import React, {useState, useEffect} from 'react'
import { motion } from 'framer-motion'
import ChatUI from './components/ChatUI'

export default function App(){
  const [topic, setTopic] = useState('')
  const [campaignId, setCampaignId] = useState(null)
  const [messages, setMessages] = useState([])
  const [isStarting, setIsStarting] = useState(false)
  const [error, setError] = useState(null)

  async function startCampaign(e){
    if (e && typeof e.preventDefault === 'function') e.preventDefault()
    if(!topic || !topic.trim()) return
    if(isStarting) return
    setIsStarting(true)
    setError(null)
    try {
      const res = await fetch('http://localhost:8000/api/start-campaign', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({topic})
      })
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const body = await res.json()
      setCampaignId(body.campaign_id)
      setMessages([{from: 'system', text: {type: 'status', message: 'Campaign started, connecting to stream...'}}])

      // connect to SSE
      const evtSrc = new EventSource(`http://localhost:8000${body.stream_url}`)
      evtSrc.onmessage = (ev) => {
        try{
          const data = JSON.parse(ev.data)
          setMessages(prev => [...prev, {from: data.agent || 'server', text: data}])
          if(data.type === 'complete') evtSrc.close()
        }catch(err){
          console.error('invalid event', err)
        }
      }
      evtSrc.onerror = (err) => {
        console.error('SSE error', err)
        evtSrc.close()
        setIsStarting(false)
        setError('Connection lost. Please try again.')
      }
    } catch (err) {
      setError(err.message)
      setIsStarting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-gray-50">
      <div className="max-w-6xl mx-auto p-6">
        {!campaignId ? (
          <motion.div 
            initial={{opacity: 0, y: -20}}
            animate={{opacity: 1, y: 0}}
            transition={{duration: 0.5}}
            className="text-center py-20"
          >
            <div className="mb-6">
              <h1 className="text-5xl font-bold text-gray-900 mb-2">
                <span className="bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
                  CampaignCraft
                </span>
              </h1>
              <p className="text-gray-600 text-lg">AI-powered sales & marketing campaign generator</p>
            </div>
            
            <form onSubmit={startCampaign} className="flex gap-2 items-center justify-center mb-4">
              <input
                className="border-2 border-gray-300 rounded-lg px-6 py-3 w-full max-w-lg focus:outline-none focus:border-blue-600 transition-colors"
                placeholder="Enter a topic to start your campaign…"
                value={topic}
                onChange={(e)=>{setTopic(e.target.value); setError(null);}}
                aria-label="campaign-topic"
                disabled={isStarting}
              />
              <motion.button
                type="submit"
                onClick={startCampaign}
                className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
                disabled={!topic.trim() || isStarting}
                whileHover={{scale: 1.05}}
                whileTap={{scale: 0.95}}
              >
                {isStarting ? (
                  <span className="flex items-center gap-2">
                    <span className="inline-block animate-spin">⚙️</span>
                    Starting…
                  </span>
                ) : 'Start Campaign'}
              </motion.button>
            </form>

            {error && (
              <motion.div 
                initial={{opacity: 0}}
                animate={{opacity: 1}}
                className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 max-w-lg mx-auto"
              >
                ❌ {error}
              </motion.div>
            )}

            <p className="text-gray-500 text-sm mt-6">
              Try: "AI automation in retail", "SaaS marketing strategy", or "B2B lead generation"
            </p>
          </motion.div>
        ) : (
          <motion.div
            initial={{opacity: 0, y: 20}}
            animate={{opacity: 1, y: 0}}
            transition={{duration: 0.3}}
          >
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-3xl font-bold text-gray-900">
                Campaign: <span className="text-blue-600">{topic}</span>
              </h2>
            </div>
            <ChatUI messages={messages} setMessages={setMessages} campaignId={campaignId} />
          </motion.div>
        )}
      </div>
    </div>
  )
}

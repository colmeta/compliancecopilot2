/**
 * CLARITY BACKEND KEEP-ALIVE SCRIPT
 * 
 * Prevents Render free tier from hibernating by pinging every 14 minutes
 * 
 * BETTER ALTERNATIVE: Use UptimeRobot (free, no hosting needed)
 * https://uptimerobot.com
 */

const cron = require('cron');
const https = require('https');

// Your actual CLARITY backend URL
const BACKEND_URL = 'https://veritas-engine-zae0.onrender.com/health';

// Ping every 14 minutes (Render sleeps after 15 min of inactivity)
const PING_INTERVAL = '*/14 * * * *';

/**
 * Pings the backend server to keep it alive
 */
const pingServer = () => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] Pinging CLARITY backend...`);
  
  https
    .get(BACKEND_URL, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        if (res.statusCode === 200) {
          console.log(`✅ [${timestamp}] Server alive! Status: ${res.statusCode}`);
          try {
            const parsed = JSON.parse(data);
            console.log(`   Response:`, parsed);
          } catch (e) {
            console.log(`   Response: ${data.substring(0, 100)}`);
          }
        } else {
          console.error(`❌ [${timestamp}] Unexpected status: ${res.statusCode}`);
        }
      });
    })
    .on('error', (err) => {
      console.error(`❌ [${timestamp}] Failed to ping:`, err.message);
    });
};

// Create cron job
const keepAliveJob = new cron.CronJob(
  PING_INTERVAL,
  pingServer,
  null,
  true,  // Start immediately
  'UTC'
);

console.log('🚀 CLARITY Keep-Alive Started');
console.log(`📍 Target: ${BACKEND_URL}`);
console.log(`⏰ Interval: Every 14 minutes`);
console.log(`🕐 Next ping: ${keepAliveJob.nextDates().toString()}`);
console.log('');

// Ping once immediately on startup
pingServer();

module.exports = {
  keepAliveJob,
  pingServer
};

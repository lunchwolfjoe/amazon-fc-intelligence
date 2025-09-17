const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3002;

// Enable CORS for all routes
app.use(cors());
app.use(express.json());

// Mock data endpoint
app.get('/api/analysis', (req, res) => {
  // Try to read real data from the reddit collector if available
  const dataPath = path.join(__dirname, '../reddit-data-collector/analysis_results.json');
  
  if (fs.existsSync(dataPath)) {
    try {
      const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
      res.json({ success: true, data });
      return;
    } catch (error) {
      console.log('Error reading real data:', error);
    }
  }
  
  // Return demo data for presentation
  res.json({
    success: true,
    data: {
      total_posts: 47,
      analysis_date: new Date().toISOString(),
      posts: [
        {
          id: '1',
          title: 'Finally got the raise announcement - $1.10 for tenured workers!',
          author: 'HappyWorker2024',
          score: 234,
          num_comments: 67,
          content: 'Just got word from management. $0.50 base raise for everyone, plus $1.10 for workers over 18 months. About time!',
          permalink: '/r/amazonfc/comments/raise_announcement/',
          created_date: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          aws_sentiment: {
            sentiment: 'positive',
            confidence: 0.924,
            estimated_cost: 0.0003,
            processing_time_ms: 72,
            emotions: { emotion: 'joy', confidence: 0.856 },
            key_phrases: { compensation_phrases: [{ text: 'raise', confidence: 0.98 }, { text: '$1.10', confidence: 0.94 }] }
          },
          sample_comments: [
            { author: 'user1', content: 'About time! When does it take effect?', sentiment: 'positive', score: 45, aws_sentiment: { sentiment: 'positive', confidence: 0.87 } },
            { author: 'user2', content: 'Finally some good news from corporate', sentiment: 'positive', score: 32, aws_sentiment: { sentiment: 'positive', confidence: 0.91 } }
          ]
        },
        {
          id: '2',
          title: '50 cents is insulting - this barely covers gas increase',
          author: 'FrustratedFC',
          score: 298,
          num_comments: 156,
          content: 'Are you kidding me? 50 cents? That\'s $20 more per week before taxes. Gas went up more than that this month.',
          permalink: '/r/amazonfc/comments/insulting_raise/',
          created_date: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
          aws_sentiment: {
            sentiment: 'negative',
            confidence: 0.967,
            estimated_cost: 0.0002,
            processing_time_ms: 68,
            emotions: { emotion: 'anger', confidence: 0.834 },
            key_phrases: { compensation_phrases: [{ text: '50 cents', confidence: 0.96 }, { text: 'insulting', confidence: 0.89 }] }
          },
          sample_comments: [
            { author: 'user3', content: 'Seriously, this is a joke', sentiment: 'negative', score: 67, aws_sentiment: { sentiment: 'negative', confidence: 0.92 } },
            { author: 'user4', content: 'Better than nothing I guess', sentiment: 'neutral', score: 23, aws_sentiment: { sentiment: 'neutral', confidence: 0.78 } }
          ]
        },
        {
          id: '3',
          title: 'Bezos makes billions while we get crumbs',
          author: 'MadAsHell',
          score: 189,
          num_comments: 143,
          content: 'This company is so greedy it\'s disgusting. We make them rich and get literal pennies in return.',
          permalink: '/r/amazonfc/comments/greedy_company/',
          created_date: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
          aws_sentiment: {
            sentiment: 'negative',
            confidence: 0.945,
            estimated_cost: 0.0002,
            processing_time_ms: 71,
            emotions: { emotion: 'anger', confidence: 0.789 },
            key_phrases: { compensation_phrases: [{ text: 'billions', confidence: 0.92 }, { text: 'crumbs', confidence: 0.88 }] }
          },
          sample_comments: [
            { author: 'user9', content: 'Corporate greed at its finest', sentiment: 'negative', score: 89, aws_sentiment: { sentiment: 'negative', confidence: 0.94 } }
          ]
        },
        {
          id: '4',
          title: 'CVG site got $0.90 for tier 3s - not bad!',
          author: 'CVG_Associate',
          score: 156,
          num_comments: 43,
          content: 'Just announced at our site. T1 gets $0.50, T3 gets $0.90. Plus they\'re adjusting step plans. Actually pretty decent.',
          permalink: '/r/amazonfc/comments/cvg_raise/',
          created_date: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
          aws_sentiment: {
            sentiment: 'positive',
            confidence: 0.887,
            estimated_cost: 0.0002,
            processing_time_ms: 65,
            emotions: { emotion: 'joy', confidence: 0.798 },
            key_phrases: { compensation_phrases: [{ text: '$0.90', confidence: 0.95 }, { text: 'tier 3', confidence: 0.91 }] }
          },
          sample_comments: [
            { author: 'user3', content: 'CVG always treats us well', sentiment: 'positive', score: 28, aws_sentiment: { sentiment: 'positive', confidence: 0.85 } }
          ]
        },
        {
          id: '5',
          title: 'This doesn\'t even cover my rent increase',
          author: 'StrugglingParent',
          score: 167,
          num_comments: 78,
          content: 'My rent went up $150 this year. This raise gives me $20 more per week. Do the math.',
          permalink: '/r/amazonfc/comments/rent_increase/',
          created_date: new Date(Date.now() - 7 * 60 * 60 * 1000).toISOString(),
          aws_sentiment: {
            sentiment: 'negative',
            confidence: 0.823,
            estimated_cost: 0.0002,
            processing_time_ms: 69,
            emotions: { emotion: 'sadness', confidence: 0.678 },
            key_phrases: { compensation_phrases: [{ text: 'rent increase', confidence: 0.89 }, { text: '$20', confidence: 0.93 }] }
          },
          sample_comments: [
            { author: 'user10', content: 'Same boat here, it\'s rough', sentiment: 'negative', score: 45, aws_sentiment: { sentiment: 'negative', confidence: 0.81 } }
          ]
        },
        {
          id: '6',
          title: 'BFL1 raise details - step plan changes too',
          author: 'BFL1_Info',
          score: 98,
          num_comments: 34,
          content: 'Official announcement: $0.50 base + step plan cap increases. Meeting at 7am tomorrow for details.',
          permalink: '/r/amazonfc/comments/bfl1_details/',
          created_date: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
          aws_sentiment: {
            sentiment: 'neutral',
            confidence: 0.876,
            estimated_cost: 0.0002,
            processing_time_ms: 64,
            emotions: { emotion: 'neutral', confidence: 0.798 }
          },
          sample_comments: [
            { author: 'user5', content: 'Thanks for the info!', sentiment: 'positive', score: 12, aws_sentiment: { sentiment: 'positive', confidence: 0.85 } }
          ]
        },
        {
          id: '7',
          title: 'Step plan increases are actually huge',
          author: 'TenuredWorker',
          score: 134,
          num_comments: 29,
          content: 'Everyone focusing on the base raise but the step plan cap increases mean way more money long term. This is actually good.',
          permalink: '/r/amazonfc/comments/step_plan_good/',
          created_date: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
          aws_sentiment: {
            sentiment: 'positive',
            confidence: 0.856,
            estimated_cost: 0.0003,
            processing_time_ms: 73,
            emotions: { emotion: 'joy', confidence: 0.723 },
            key_phrases: { compensation_phrases: [{ text: 'step plan', confidence: 0.96 }, { text: 'long term', confidence: 0.84 }] }
          },
          sample_comments: [
            { author: 'user4', content: 'Exactly! People don\'t understand the math', sentiment: 'positive', score: 22, aws_sentiment: { sentiment: 'positive', confidence: 0.89 } }
          ]
        },
        {
          id: '8',
          title: 'Mixed feelings about this raise',
          author: 'ConflictedWorker',
          score: 78,
          num_comments: 34,
          content: 'Happy we got something but disappointed it\'s not more. Better than nothing but still not enough.',
          permalink: '/r/amazonfc/comments/mixed_feelings/',
          created_date: new Date(Date.now() - 9 * 60 * 60 * 1000).toISOString(),
          aws_sentiment: {
            sentiment: 'mixed',
            confidence: 0.723,
            estimated_cost: 0.0002,
            processing_time_ms: 67,
            emotions: { emotion: 'confusion', confidence: 0.645 },
            key_phrases: { compensation_phrases: [{ text: 'raise', confidence: 0.91 }] }
          },
          sample_comments: [
            { author: 'user18', content: 'Exactly how I feel', sentiment: 'mixed', score: 12, aws_sentiment: { sentiment: 'mixed', confidence: 0.67 } }
          ]
        }
      ],
      aws_sentiment_summary: {
        positive: 18,
        negative: 12,
        neutral: 15,
        mixed: 2
      },
      cost_data: {
        daily_limit: 5.00,
        current_daily_spend: 0.0234,
        cache_savings: 0.0089,
        total_requests: 47,
        cache_hits: 13,
        aws_requests: 34
      },
      emotion_breakdown: [
        { emotion: 'joy', confidence: 0.342, count: 18, avg_upvotes: 89.3 },
        { emotion: 'anger', confidence: 0.256, count: 12, avg_upvotes: 127.8 },
        { emotion: 'neutral', confidence: 0.298, count: 15, avg_upvotes: 45.2 },
        { emotion: 'sadness', confidence: 0.089, count: 2, avg_upvotes: 67.4 }
      ],
      posts_by_sentiment: {
        positive: [
          {
            id: 'pos1',
            title: 'Finally got the raise announcement - $1.10 for tenured workers!',
            author: 'HappyWorker2024',
            score: 234,
            num_comments: 67,
            content: 'Just got word from management. $0.50 base raise for everyone, plus $1.10 for workers over 18 months. About time!',
            permalink: '/r/amazonfc/comments/raise_announcement/',
            aws_sentiment: { sentiment: 'positive', confidence: 0.924, emotions: { emotion: 'joy', confidence: 0.856 } },
            sample_comments: [
              { author: 'user1', content: 'About time! When does it take effect?', sentiment: 'positive', score: 45, aws_sentiment: { sentiment: 'positive', confidence: 0.87 } },
              { author: 'user2', content: 'Finally some good news from corporate', sentiment: 'positive', score: 32, aws_sentiment: { sentiment: 'positive', confidence: 0.91 } }
            ]
          },
          {
            id: 'pos2',
            title: 'CVG site got $0.90 for tier 3s - not bad!',
            author: 'CVG_Associate',
            score: 156,
            num_comments: 43,
            content: 'Just announced at our site. T1 gets $0.50, T3 gets $0.90. Plus they\'re adjusting step plans. Actually pretty decent.',
            permalink: '/r/amazonfc/comments/cvg_raise/',
            aws_sentiment: { sentiment: 'positive', confidence: 0.887, emotions: { emotion: 'joy', confidence: 0.798 } },
            sample_comments: [
              { author: 'user3', content: 'CVG always treats us well', sentiment: 'positive', score: 28, aws_sentiment: { sentiment: 'positive', confidence: 0.85 } }
            ]
          },
          {
            id: 'pos3',
            title: 'Step plan increases are actually huge',
            author: 'TenuredWorker',
            score: 134,
            num_comments: 29,
            content: 'Everyone focusing on the base raise but the step plan cap increases mean way more money long term. This is actually good.',
            permalink: '/r/amazonfc/comments/step_plan_good/',
            aws_sentiment: { sentiment: 'positive', confidence: 0.856, emotions: { emotion: 'joy', confidence: 0.723 } },
            sample_comments: [
              { author: 'user4', content: 'Exactly! People don\'t understand the math', sentiment: 'positive', score: 22, aws_sentiment: { sentiment: 'positive', confidence: 0.89 } }
            ]
          },
          {
            id: 'pos4',
            title: 'BFL1 - Better than expected honestly',
            author: 'BFL1_Worker',
            score: 89,
            num_comments: 18,
            content: 'Thought we\'d get 25 cents like last time. $0.50 plus step changes is actually not terrible for once.',
            permalink: '/r/amazonfc/comments/bfl1_better/',
            aws_sentiment: { sentiment: 'positive', confidence: 0.798, emotions: { emotion: 'surprise', confidence: 0.645 } },
            sample_comments: [
              { author: 'user5', content: 'Same, pleasantly surprised', sentiment: 'positive', score: 15, aws_sentiment: { sentiment: 'positive', confidence: 0.82 } }
            ]
          },
          {
            id: 'pos5',
            title: 'Thank you Amazon for listening to us',
            author: 'GratefulAA',
            score: 67,
            num_comments: 12,
            content: 'I know it\'s not huge but at least they gave us something. With inflation this helps a bit.',
            permalink: '/r/amazonfc/comments/grateful/',
            aws_sentiment: { sentiment: 'positive', confidence: 0.734, emotions: { emotion: 'joy', confidence: 0.567 } },
            sample_comments: [
              { author: 'user6', content: 'Every little bit helps', sentiment: 'positive', score: 8, aws_sentiment: { sentiment: 'positive', confidence: 0.76 } }
            ]
          }
        ],
        negative: [
          {
            id: 'neg1',
            title: '50 cents is insulting - this barely covers gas increase',
            author: 'FrustratedFC',
            score: 189,
            num_comments: 143,
            content: 'Are you kidding me? 50 cents? That\'s $20 more per week before taxes. Gas went up more than that this month.',
            permalink: '/r/amazonfc/comments/insulting_raise/',
            aws_sentiment: { sentiment: 'negative', confidence: 0.967, emotions: { emotion: 'anger', confidence: 0.834 } },
            sample_comments: [
              { author: 'user7', content: 'Seriously, this is a joke', sentiment: 'negative', score: 67, aws_sentiment: { sentiment: 'negative', confidence: 0.92 } },
              { author: 'user8', content: 'Better than nothing I guess', sentiment: 'neutral', score: 23, aws_sentiment: { sentiment: 'neutral', confidence: 0.78 } }
            ]
          },
          {
            id: 'neg2',
            title: 'Bezos makes billions while we get crumbs',
            author: 'MadAsHell',
            score: 298,
            num_comments: 156,
            content: 'This company is so greedy it\'s disgusting. We make them rich and get literal pennies in return.',
            permalink: '/r/amazonfc/comments/greedy_company/',
            aws_sentiment: { sentiment: 'negative', confidence: 0.945, emotions: { emotion: 'anger', confidence: 0.789 } },
            sample_comments: [
              { author: 'user9', content: 'Corporate greed at its finest', sentiment: 'negative', score: 89, aws_sentiment: { sentiment: 'negative', confidence: 0.94 } }
            ]
          },
          {
            id: 'neg3',
            title: 'This doesn\'t even cover my rent increase',
            author: 'StrugglingParent',
            score: 167,
            num_comments: 78,
            content: 'My rent went up $150 this year. This raise gives me $20 more per week. Do the math.',
            permalink: '/r/amazonfc/comments/rent_increase/',
            aws_sentiment: { sentiment: 'negative', confidence: 0.823, emotions: { emotion: 'sadness', confidence: 0.678 } },
            sample_comments: [
              { author: 'user10', content: 'Same boat here, it\'s rough', sentiment: 'negative', score: 45, aws_sentiment: { sentiment: 'negative', confidence: 0.81 } }
            ]
          },
          {
            id: 'neg4',
            title: 'Inflation ate this raise 2 years ago',
            author: 'EconomicsGuy',
            score: 145,
            num_comments: 67,
            content: 'Everything costs 20% more than 2 years ago. This 3% raise is actually a pay cut in real terms.',
            permalink: '/r/amazonfc/comments/inflation_ate_it/',
            aws_sentiment: { sentiment: 'negative', confidence: 0.789, emotions: { emotion: 'anger', confidence: 0.623 } },
            sample_comments: [
              { author: 'user11', content: 'Math checks out unfortunately', sentiment: 'negative', score: 34, aws_sentiment: { sentiment: 'negative', confidence: 0.76 } }
            ]
          },
          {
            id: 'neg5',
            title: 'They can afford to pay us more',
            author: 'UnionSupporter',
            score: 123,
            num_comments: 89,
            content: 'Record profits every quarter but they give us scraps. We need to organize.',
            permalink: '/r/amazonfc/comments/organize/',
            aws_sentiment: { sentiment: 'negative', confidence: 0.756, emotions: { emotion: 'anger', confidence: 0.589 } },
            sample_comments: [
              { author: 'user12', content: 'Time for collective action', sentiment: 'negative', score: 56, aws_sentiment: { sentiment: 'negative', confidence: 0.83 } }
            ]
          }
        ],
        neutral: [
          {
            id: 'neu1',
            title: 'BFL1 raise details - step plan changes too',
            author: 'BFL1_Info',
            score: 98,
            num_comments: 34,
            content: 'Official announcement: $0.50 base + step plan cap increases. Meeting at 7am tomorrow for details.',
            permalink: '/r/amazonfc/comments/bfl1_details/',
            aws_sentiment: { sentiment: 'neutral', confidence: 0.876, emotions: { emotion: 'neutral', confidence: 0.798 } },
            sample_comments: [
              { author: 'user13', content: 'Thanks for the info!', sentiment: 'positive', score: 12, aws_sentiment: { sentiment: 'positive', confidence: 0.85 } }
            ]
          },
          {
            id: 'neu2',
            title: 'CMH3 raise meeting tomorrow at 7am',
            author: 'CMH3_Curious',
            score: 67,
            num_comments: 23,
            content: 'Still waiting to hear anything official from management. Anyone else at CMH3 get details?',
            permalink: '/r/amazonfc/comments/cmh3_meeting/',
            aws_sentiment: { sentiment: 'neutral', confidence: 0.834, emotions: { emotion: 'neutral', confidence: 0.756 } },
            sample_comments: [
              { author: 'user14', content: 'Nothing yet, meeting is tomorrow', sentiment: 'neutral', score: 8, aws_sentiment: { sentiment: 'neutral', confidence: 0.82 } }
            ]
          },
          {
            id: 'neu3',
            title: 'When do we get updates on NJ sites?',
            author: 'NJ_Worker',
            score: 45,
            num_comments: 18,
            content: 'Seeing all these other states getting news. Anyone in NJ hear anything yet?',
            permalink: '/r/amazonfc/comments/nj_updates/',
            aws_sentiment: { sentiment: 'neutral', confidence: 0.798, emotions: { emotion: 'neutral', confidence: 0.723 } },
            sample_comments: [
              { author: 'user15', content: 'EWR4 had their meeting yesterday', sentiment: 'neutral', score: 5, aws_sentiment: { sentiment: 'neutral', confidence: 0.79 } }
            ]
          },
          {
            id: 'neu4',
            title: 'Raise effective date?',
            author: 'PayrollQuestion',
            score: 34,
            num_comments: 15,
            content: 'Does anyone know when the raise takes effect? Next paycheck or start of next month?',
            permalink: '/r/amazonfc/comments/effective_date/',
            aws_sentiment: { sentiment: 'neutral', confidence: 0.812, emotions: { emotion: 'neutral', confidence: 0.734 } },
            sample_comments: [
              { author: 'user16', content: 'Usually next pay period', sentiment: 'neutral', score: 7, aws_sentiment: { sentiment: 'neutral', confidence: 0.85 } }
            ]
          },
          {
            id: 'neu5',
            title: 'Texas sites - any word yet?',
            author: 'TexasFC',
            score: 29,
            num_comments: 12,
            content: 'HOU8 here. Heard different amounts from different people. What\'s official?',
            permalink: '/r/amazonfc/comments/texas_sites/',
            aws_sentiment: { sentiment: 'neutral', confidence: 0.789, emotions: { emotion: 'neutral', confidence: 0.698 } },
            sample_comments: [
              { author: 'user17', content: 'HOU2 got $0.50 base', sentiment: 'neutral', score: 4, aws_sentiment: { sentiment: 'neutral', confidence: 0.81 } }
            ]
          }
        ],
        mixed: [
          {
            id: 'mix1',
            title: 'Mixed feelings about this raise',
            author: 'ConflictedWorker',
            score: 78,
            num_comments: 34,
            content: 'Happy we got something but disappointed it\'s not more. Better than nothing but still not enough.',
            permalink: '/r/amazonfc/comments/mixed_feelings/',
            aws_sentiment: { sentiment: 'mixed', confidence: 0.723, emotions: { emotion: 'confusion', confidence: 0.645 } },
            sample_comments: [
              { author: 'user18', content: 'Exactly how I feel', sentiment: 'mixed', score: 12, aws_sentiment: { sentiment: 'mixed', confidence: 0.67 } }
            ]
          },
          {
            id: 'mix2',
            title: 'Good news bad news situation',
            author: 'RealistWorker',
            score: 56,
            num_comments: 28,
            content: 'Good: We got a raise. Bad: It\'s barely anything. Good: Step plan changes. Bad: Still underpaid.',
            permalink: '/r/amazonfc/comments/good_bad/',
            aws_sentiment: { sentiment: 'mixed', confidence: 0.689, emotions: { emotion: 'confusion', confidence: 0.578 } },
            sample_comments: [
              { author: 'user19', content: 'Life at Amazon in a nutshell', sentiment: 'mixed', score: 9, aws_sentiment: { sentiment: 'mixed', confidence: 0.71 } }
            ]
          }
        ]
      },
      posts_by_emotion: {
        joy: [
          {
            id: 'joy1',
            title: 'Finally got the raise announcement - $1.10 for tenured workers!',
            author: 'HappyWorker2024',
            score: 234,
            num_comments: 67,
            content: 'Just got word from management. $0.50 base raise for everyone, plus $1.10 for workers over 18 months. About time!',
            aws_sentiment: { sentiment: 'positive', confidence: 0.924, emotions: { emotion: 'joy', confidence: 0.856 } }
          },
          {
            id: 'joy2',
            title: 'CVG site got $0.90 for tier 3s - not bad!',
            author: 'CVG_Associate',
            score: 156,
            num_comments: 43,
            content: 'Just announced at our site. T1 gets $0.50, T3 gets $0.90. Plus they\'re adjusting step plans. Actually pretty decent.',
            aws_sentiment: { sentiment: 'positive', confidence: 0.887, emotions: { emotion: 'joy', confidence: 0.798 } }
          },
          {
            id: 'joy3',
            title: 'Step plan increases are actually huge',
            author: 'TenuredWorker',
            score: 134,
            num_comments: 29,
            content: 'Everyone focusing on the base raise but the step plan cap increases mean way more money long term. This is actually good.',
            aws_sentiment: { sentiment: 'positive', confidence: 0.856, emotions: { emotion: 'joy', confidence: 0.723 } }
          }
        ],
        anger: [
          {
            id: 'anger1',
            title: '50 cents is insulting - this barely covers gas increase',
            author: 'FrustratedFC',
            score: 298,
            num_comments: 156,
            content: 'Are you kidding me? 50 cents? That\'s $20 more per week before taxes. Gas went up more than that this month.',
            aws_sentiment: { sentiment: 'negative', confidence: 0.967, emotions: { emotion: 'anger', confidence: 0.834 } }
          },
          {
            id: 'anger2',
            title: 'Bezos makes billions while we get crumbs',
            author: 'MadAsHell',
            score: 189,
            num_comments: 143,
            content: 'This company is so greedy it\'s disgusting. We make them rich and get literal pennies in return.',
            aws_sentiment: { sentiment: 'negative', confidence: 0.945, emotions: { emotion: 'anger', confidence: 0.789 } }
          },
          {
            id: 'anger3',
            title: 'They can afford to pay us more',
            author: 'UnionSupporter',
            score: 123,
            num_comments: 89,
            content: 'Record profits every quarter but they give us scraps. We need to organize.',
            aws_sentiment: { sentiment: 'negative', confidence: 0.756, emotions: { emotion: 'anger', confidence: 0.589 } }
          }
        ],
        sadness: [
          {
            id: 'sad1',
            title: 'This doesn\'t even cover my rent increase',
            author: 'StrugglingParent',
            score: 167,
            num_comments: 78,
            content: 'My rent went up $150 this year. This raise gives me $20 more per week. Do the math.',
            aws_sentiment: { sentiment: 'negative', confidence: 0.823, emotions: { emotion: 'sadness', confidence: 0.678 } }
          },
          {
            id: 'sad2',
            title: 'Can barely afford groceries as is',
            author: 'SingleMom',
            score: 89,
            num_comments: 45,
            content: 'I was hoping for something that would actually help with bills. This doesn\'t even cover the grocery price increases.',
            aws_sentiment: { sentiment: 'negative', confidence: 0.789, emotions: { emotion: 'sadness', confidence: 0.634 } }
          }
        ],
        neutral: [
          {
            id: 'neu1',
            title: 'BFL1 raise details - step plan changes too',
            author: 'BFL1_Info',
            score: 98,
            num_comments: 34,
            content: 'Official announcement: $0.50 base + step plan cap increases. Meeting at 7am tomorrow for details.',
            aws_sentiment: { sentiment: 'neutral', confidence: 0.876, emotions: { emotion: 'neutral', confidence: 0.798 } }
          },
          {
            id: 'neu2',
            title: 'CMH3 raise meeting tomorrow at 7am',
            author: 'CMH3_Curious',
            score: 67,
            num_comments: 23,
            content: 'Still waiting to hear anything official from management. Anyone else at CMH3 get details?',
            aws_sentiment: { sentiment: 'neutral', confidence: 0.834, emotions: { emotion: 'neutral', confidence: 0.756 } }
          }
        ],
        surprise: [
          {
            id: 'surprise1',
            title: 'Wait, we\'re actually getting MORE than expected?',
            author: 'ShockedWorker',
            score: 178,
            num_comments: 89,
            content: 'I thought it would be 25 cents like last time. $0.50 plus step plan changes is actually not terrible.',
            aws_sentiment: { sentiment: 'positive', confidence: 0.723, emotions: { emotion: 'surprise', confidence: 0.645 } }
          }
        ],
        confusion: [
          {
            id: 'conf1',
            title: 'Mixed feelings about this raise',
            author: 'ConflictedWorker',
            score: 78,
            num_comments: 34,
            content: 'Happy we got something but disappointed it\'s not more. Better than nothing but still not enough.',
            aws_sentiment: { sentiment: 'mixed', confidence: 0.723, emotions: { emotion: 'confusion', confidence: 0.645 } }
          }
        ]
      }
    }
  });
});

// Mock collection endpoint
app.post('/api/collect', (req, res) => {
  // Simulate collection process
  setTimeout(() => {
    res.json({
      success: true,
      message: 'Data collection completed',
      posts_collected: 0
    });
  }, 1000);
});

app.listen(PORT, () => {
  console.log(`API server running on http://localhost:${PORT}`);
  console.log('Endpoints:');
  console.log('  GET /api/analysis - Get analysis data');
  console.log('  POST /api/collect - Trigger data collection');
});
import numpy as np
from sklearn.utils import shuffle
import matplotlib.pyplot as plt

instances={    #所有样例的工件数和机器数
    0:[11,5],1:[6,8],2:[11,4],3:[14,5],4:[16,4],5:[10,6],
    6:[20,10],7:[20,15],8:[20,5],9:[20,15],10:[50,10]
}

class jobshop:
    def __init__(self):
        instance=6                    #获取的样例
        job,machine=instances[instance][0],instances[instance][1]  #工件数和机器数
        max_iteration=1000            #最高迭代次数
        temperature,coef=100,0.9      #默认起始温度和衰减系数
        self.min_temperature=0.1      #最低预定的温度
        '''根据工件数和机器个数调整起始温度和衰减系数'''
        if job<=11 and machine<10:    #工件数小于等于11且机器数小于10
            temperature=100    
            coef=0.9
        elif job>11 and machine<10:   #工件数大于11且机器数小于10
            temperature=500
            coef=0.99
        elif job>11 and machine>=10:  #工件数大于11且机器数大于等于10
            temperature=1000
            coef=0.99
        #self.boltzmann_const=1.380649*1e-23
        self.getData(instance=instance)   
        self.SA(self.objective,max_iteration,coef,temperature)  
        self.getFigure(instance=instance)    
    
    def getData(self,instance):   #读入文件获取数据,instance为执行的样例
        read=-1
        line_arr=[]
        full_arr=[]
        with open('data.txt','r') as f:
            for line in f.readlines():
                if 'instance '+str(instance) in line:
                    read+=1
                    continue
                if read==0:
                    read+=1
                    continue
                if read==1:
                    if '+' in line:
                        break
                    while '  ' in line or '   ' in line:
                        line=line.replace('  ',' ')
                        line=line.replace('   ',' ')
                    temp=line.split(' ')
                    temp=[str.strip() for str in temp]
                    for i in range(len(temp)):
                        if i%2!=0:
                            line_arr.append(float(temp[i]))   
                    full_arr.append(line_arr)  
                    line_arr=[]
        self.time=full_arr  
        print("{0:-^104}".format('Instance '+str(instance)))  
     
    def getRandom(self):   #随机获取新解（机器的新顺序）
        r=np.arange(len(self.time))
        r=shuffle(r)
        return r

    def getNeighbour(self,x):  #获取邻域解
        n=len(x)
        a,b=np.random.randint(n),np.random.randint(n)
        if a==b:
            a,b=np.random.randint(n),np.random.randint(n)
        else:         
            temp=x[a]
            x[a]=x[b]
            x[b]=temp
        return x

    def objective(self,x):   #定义目标函数,返回所有工件的加工时间
        n,m=len(self.time),len(self.time[0])
        cost=[[0]*m]*n
        for i in range(n):
            for j in range(m):
                if x[i]==x[0] and j==0:   #下标 0,0
                    cost[x[i]][j]=self.time[x[i]][j]
                elif x[i]==x[0] and j!=0:
                    cost[x[i]][j]=cost[x[i]][j-1]+self.time[x[i]][j]
                elif x[i]!=x[0] and j==0:
                    cost[x[i]][j]=cost[x[i-1]][j]+self.time[x[i]][j]
                else:
                    cost[x[i]][j]=max(cost[x[i]][j-1],cost[x[i-1]][j])+self.time[x[i]][j]
        self.order=x
        return cost[n-1][m-1]   
            
    def SA(self,objective,max_iteration,coef,temperature):  #模拟退火算法
        initial_x=self.getRandom()              #随机获取新解和目标函数值
        initial_cost=objective(initial_x)       
        best_cost=initial_cost
        self.output,best_order=[],[]
        self.output.append(initial_cost)        #记录每次最新的最优加工时间
        probability=0                           #初始化 Metropolis 准则概率
        while temperature>self.min_temperature:    #终止迭代的条件:温度大于预定的最低温度
            for i in range(max_iteration):
                new_x=self.getNeighbour(initial_x)  #获取起始点/候选极值点的邻域解
                new_cost=objective(new_x)
                if new_cost<initial_cost:      #若新目标函数值小于起始目标函数值,则接受x作为新候选极值点
                    initial_cost=new_cost     
                    initial_x=new_x                             
                    if new_cost<best_cost:     #更新每次最优的加工时间和加工顺序           
                        best_order,best_cost=self.order,new_cost
                        print(f'Acceptance Criteria={probability:.5f} | Temperature={temperature:.2f} | Order={best_order} | Time={best_cost}')
                        self.output.append(best_cost)
                else:   
                    difference=initial_cost-new_cost    #计算 Metropolis 准则概率
                    probability=np.exp(difference/(temperature))
                    if np.random.random()<probability:   #若符合该准则,则接受x作为新候选极值点
                        initial_cost=new_cost
                        initial_x=new_x
            initial_x=self.getRandom()                  #定义新解（新顺序）
            initial_cost=self.objective(initial_x)      
            temperature=temperature*coef                #下调温度
        print(f'Terminate Temperature={temperature:.3f}\nBest Order={best_order}\nBest Time={best_cost}') 

    def getFigure(self,instance):    #可视化数据：加工时间下降（目标函数）
        plt.title('Job-shop Scheduling Instance '+str(instance))
        plt.plot(self.output,'ro-')
        plt.xlabel('Count')
        plt.ylabel('Time taken (Objective Function)')
        plt.show()

if __name__=='__main__':
    jobshop()
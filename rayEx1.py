import ray
import psutil
# num_cpus = psutil.cpu_count(logical=False)
num_cpus = len(psutil.Process().cpu_affinity())
print('Initializing Ray on {} cpus.'.format(num_cpus))
ray.init(num_cpus=num_cpus)
print('Ray initialization {} on {} cores.'.format('successful' if ray.is_initialized() else 'failed', num_cpus))

@ray.remote
class MyActor(object):
    def __init__(self):
        pass
    def func(self, x):
        np.savetxt('{}.txt'.format(x),x)
        print(x**2)


actors = [MyActor.remote() for _ in range(num_cpus)]
actor_pool = ray.util.ActorPool(actors)

def ray_batch(args_list):
    actor_pool.map(lambda a, v: a.func.remote(v), [v for v in args_list])


args_list = [range(10)]
ray_batch(args_list)
#print(ray.get_actor(results_list))

from versionclimber import liquid, liquidparser


env = liquid.YAMLEnv('config.yaml')
solutions = env.run(liquidparser)

print('\n' * 5)
print('Solution is:')
for sol in solutions:
    print(sol)

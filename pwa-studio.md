PR: https://github.com/magento/pwa-studio/pull/743

## Setup Projeto
```
cd projects
git clone https://github.com/magento/pwa-studio.git
cd pwa-studio
git checkout b6f4118b011a92252504d4edaa6596748d776d7d # versão anterior ao fix
nvm use 10 # segundo arquivo pwa-studio/.circleci/config.yml
npm install
npm test # jest
```

## Reported flaky tests
```
npx jest packages/venia-concept/src/components/CategoryList/__tests__/categoryList.spec.js -t "renders category tiles" --coverage=false
npx jest packages/venia-concept/src/components/CreateAccount/__tests__/createAccount.spec.js -t "executes validators on submit" --coverage=false
npx jest packages/venia-concept/src/components/CreateAccount/__tests__/createAccount.spec.js -t "calls onSubmit if validation passes" --coverage=false
npx jest packages/venia-concept/src/components/Navigation/__tests__/categoryTree.spec.js -t "child node correctly sets new root and parent ids" --coverage=false
```


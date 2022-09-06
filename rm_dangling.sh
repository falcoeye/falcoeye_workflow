docker images --quiet --filter=dangling=true | (grep -v ^deploy || echo :) | xargs docker rmi
